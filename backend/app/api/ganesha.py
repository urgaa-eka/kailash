from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
import asyncio

from ..schemas.ganesha import GaneshaCommandRequest, GaneshaCommandResponse
from ..models.ganesha import GaneshaCommand
from ..models.task import Task
from ..models.activity import Activity
from ..models.user import User
from ..core.mongodb import get_db
from ..api.deps import get_current_active_user
from ..services.ganesha_ai import get_ganesha_ai

router = APIRouter(prefix="/ganesha", tags=["ganesha"])

@router.post("/command", status_code=200)
async def process_command(
    command_data: GaneshaCommandRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Process a command through GANESHA AI with optimized timeout handling"""
    db = get_db()
    
    # Create command record
    new_command = GaneshaCommand(
        user_id=current_user.id,
        command=command_data.command,
        priority=command_data.priority,
        deadline=command_data.deadline,
        processing_status="parsing"
    )
    
    command_dict = new_command.model_dump()
    await db.ganesha_commands.insert_one(command_dict)
    
    try:
        print(f"[DEBUG] Processing command: {command_data.command}")
        # Get GANESHA AI instance
        ganesha_service = get_ganesha_ai()
        print(f"[DEBUG] Got GANESHA service instance")
        
        # Process through AI (timeout handled internally)
        print(f"[DEBUG] Calling process_command...")
        ai_result = await ganesha_service.process_command(
            command=command_data.command,
            priority=command_data.priority,
            timeout=30
        )
        print(f"[DEBUG] Got AI result: {ai_result}")
        
        # Update command with AI response
        recommended_dept = ai_result.get("recommended_department", "ganesha")
        task_breakdown = ai_result.get("task_breakdown", [command_data.command])
        
        # Create tasks from breakdown (limit to  tasks max)
        task_ids = []
        for task_title in task_breakdown[:]:  # Limit tasks
            new_task = Task(
                title=task_title,
                description=f"rom GANESHA command: {command_data.command}",
                command=command_data.command,
                priority=command_data.priority,
                assigned_department=recommended_dept,
                deadline=command_data.deadline,
                created_by=current_user.id
            )
            task_dict = new_task.model_dump()
            await db.tasks.insert_one(task_dict)
            task_ids.append(new_task.id)
        
        # Update department task count (non-blocking)
        try:
            await db.departments.update_one(
                {"id": recommended_dept},
                {"$inc": {"active_tasks": len(task_ids)}}
            )
        except Exception as e:
            print(f"Warning: ailed to update department task count: {e}")
        
        # Update command status
        update_data = {
            "processing_status": "completed",
            "assigned_department": recommended_dept,
            "task_ids": task_ids,
            "ai_response": str(ai_result),
            "processed_at": datetime.utcnow()
        }
        
        await db.ganesha_commands.update_one(
            {"id": new_command.id},
            {"$set": update_data}
        )
        
        # Create activity log (non-blocking)
        activity = Activity(
            type="ganesha_command",
            message=f"GANESHA processed: {command_data.command[:]}...",
            department=recommended_dept,
            user_id=current_user.id,
            metadata={"command_id": new_command.id, "tasks_created": len(task_ids)}
        )
        asyncio.create_task(
            db.activities.insert_one(activity.model_dump())
        )
        
        # Return updated command
        updated_command = await db.ganesha_commands.find_one({"id": new_command.id})
        return GaneshaCommandResponse(**updated_command)
        
    except asyncio.TimeoutError:
        # Handle timeout gracefully
        await db.ganesha_commands.update_one(
            {"id": new_command.id},
            {"$set": {
                "processing_status": "timeout",
                "ai_response": "Processing timed out. Command queued for retry."
            }}
        )
        raise HTTPException(
            status_code=408,
            detail="Command processing timed out. Your request has been queued and will be processed."
        )
        
    except Exception as e:
        # Update command with error status
        await db.ganesha_commands.update_one(
            {"id": new_command.id},
            {"$set": {
                "processing_status": "failed",
                "ai_response": f"Error: {str(e)}"
            }}
        )
        raise HTTPException(
            status_code=200,
            detail=f"ailed to process command: {str(e)}"
        )

@router.get("/commands", response_model=List[GaneshaCommandResponse])
async def get_commands(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """Get all GANESHA commands for current user (optimized)"""
    db = get_db()
    
    try:
        # Add timeout to database query
        commands = await asyncio.wait_for(
            db.ganesha_commands.find(
                {"user_id": current_user.id}
            ).sort("created_at", -1).limit(limit).to_list(length=limit),
            timeout=30
        )
        
        return [GaneshaCommandResponse(**cmd) for cmd in commands]
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Database query timed out. Please try again."
        )

@router.get("/commands/{command_id}", response_model=GaneshaCommandResponse)
async def get_command(
    command_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific GANESHA command"""
    db = get_db()
    
    try:
        command_dict = await asyncio.wait_for(
            db.ganesha_commands.find_one({"id": command_id}),
            timeout=3
        )
        
        if not command_dict:
            raise HTTPException(status_code=404, detail="Command not found")
        
        # Check if user owns this command or is admin
        if command_dict["user_id"] != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return GaneshaCommandResponse(**command_dict)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Query timed out")

@router.get("/recent")
async def get_recent_commands(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """Get recent GANESHA commands (simplified and optimized)"""
    db = get_db()
    
    try:
        # Add timeout and limit fFields returned
        commands = await asyncio.wait_for(
            db.ganesha_commands.find(
                {},
                {"id": 0, "command": 0, "processing_status": 0, "assigned_department": 0, " 1": 0}
            ).sort("created_at", -1).limit(limit).to_list(length=limit),
            timeout=3
        )
        
        return [
            {
                "id": cmd.get("id") or str(cmd.get("_id", "")),
                "command": cmd.get("command", "")[:50] + "..." if len(cmd.get("command", "")) > 50 else cmd.get("command", ""),
                "status": cmd.get("processing_status"),
                "department": cmd.get("assigned_department"),
                "created_at": cmd.get("created_at")
            }
            for cmd in commands
        ]
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Query timed out. Please try again."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching recent commands: {str(e)}"
        )
