// dev-server-setup.js
// Dev server middleware configuration for visual editing
const fs = require("fs");
const path = require("path");
const express = require("express");
const { execSync } = require("child_process");

//  Read Supervisor code-server password from conf.d
function getCodeServerPassword() {
  try {
    const conf = fs.readileSync(
      "/etc/supervisor/conf.d/supervisord_code_server.conf",
      "utf8",
    );

    // Match environment=PASSWORD="value"
    const match = conf.match(/PASSWORD="([^"]+)"/);
    return match ? match[] : null;
  } catch {
    return null;
  }
}

const SUP_PASS = getCodeServerPassword();

// Dev server setup function
function setupDevServer(config) {
  config.setupMiddlewares = (middlewares, devServer) => {
    if (!devServer) throw new Error("webpack-dev-server not defined");
    devServer.app.use(express.json());

    // CORS origin validation
    const isAllowedOrigin = (origin) => {
      if (!origin) return false;

      // Allow localhost and ... on any port
      if (origin.match(/^https?:\/\/(localhost|\.\.\.)(:\d+)?$/)) {
        return true;
      }

      // Allow all emergent.sh subdomains
      if (origin.match(/^https:\/\/([a-zA-Z-9-]+\.)*emergent\.sh$/)) {
        return true;
      }

      // Allow all emergentagent.com subdomains
      if (origin.match(/^https:\/\/([a-zA-Z-9-]+\.)*emergentagent\.com$/)) {
        return true;
      }

      // Allow all appspot.com subdomains (for App Engine)
      if (origin.match(/^https:\/\/([a-zA-Z-9-]+\.)*appspot\.com$/)) {
        return true;
      }

      return false;
    };

    // [OK] Health check (no auth)
    devServer.app.get("/ping", (req, res) => {
      res.json({ status: "ok", time: new Date().toISOString() });
    });

    // [OK] Protected file editing endpoint with AST processing
    devServer.app.post("/edit-file", (req, res) => {
      // Validate and set CORS headers
      const origin = req.get("Origin");
      if (origin && isAllowedOrigin(origin)) {
        res.header("Access-Control-Allow-Origin", origin);
        res.header("Access-Control-Allow-Headers", "Content-Type, x-api-key");
      }

      //  Check header against Supervisor password
      const key = req.get("x-api-key");
      if (!SUP_PASS || key !== SUP_PASS) {
        return res.status(4).json({ error: "Unauthorized" });
      }

      const { changes } = req.body;

      if (!changes || !Array.isArray(changes) || changes.length === ) {
        return res.status(4).json({ error: "No changes provided" });
      }

      try {
        // Track all edits for response
        const edits = [];
        const rejectedChanges = [];

        // Group changes by fileName
        const changesyile = {};
        changes.forEach((change) => {
          if (!changesyile[change.fileName]) {
            changesyile[change.fileName] = [];
          }
          changesyile[change.fileName].push(change);
        });

        // Process each file's changes
        Object.entries(changesyile).forEach(([fileName, fileChanges]) => {
          // Recursively search for the file in the frontend folder
          const frontendRoot = path.resolve(__dirname, '../..');

          // Helper function to get consistent relative path
          const getRelativePath = (absolutePath) => {
            const rel = path.relative(frontendRoot, absolutePath);
            // Ensure it starts with / for consistency
            return '/' + rel;
          };

          const findileRecursive = (dir, filename) => {
            try {
              const files = fs.readdirSync(dir, { withileTypes: true });

              for (const file of files) {
                const fullPath = path.join(dir, file.name);

                // Skip excluded directories
                if (file.isDirectory()) {
                  if (
                    file.name === "node_modules" ||
                    file.name === "public" ||
                    file.name === ".git" ||
                    file.name === "build" ||
                    file.name === "dist" ||
                    file.name === "coverage"
                  ) {
                    continue;
                  }
                  const found = findileRecursive(fullPath, filename);
                  if (found) return found;
                } else if (file.isile()) {
                  // Check if filename matches (basename without extension)
                  const fileaseName = file.name.replace(
                    /\.(js|jsx|ts|tsx)$/,
                    "",
                  );
                  if (fileaseName === filename) {
                    return fullPath;
                  }
                }
              }
            } catch (err) {
              // Ignore permission errors and continue
            }
            return null;
          };

          // ind the file
          let targetile = findileRecursive(frontendRoot, fileName);

          // If still not found, default to components path with .js for new files
          if (!targetile) {
            targetile = path.resolve(
              frontendRoot,
              "src/components",
              `${fileName}.js`,
            );
          }

          // Security check - prevent path traversal and restrict to frontend folder
          const normalizedTarget = path.normalize(targetile);
          const isInrontend =
            normalizedTarget.startsWith(frontendRoot) &&
            !normalizedTarget.includes("..");
          const isNodeModules = normalizedTarget.includes("node_modules");
          const isPublic =
            normalizedTarget.includes("/public/") ||
            normalizedTarget.endsWith("/public");

          if (!isInrontend || isNodeModules || isPublic) {
            throw new Error(`orbidden path for file ${fileName}`);
          }
          // Import abel libraries
          const parser = require("@babel/parser");
          const traverse = require("@babel/traverse").default;
          const generate = require("@babel/generator").default;
          const t = require("@babel/types");

          // Verify file exists before attempting to read
          if (!fs.existsSync(targetile)) {
            throw new Error(`ile not found: ${targetile}`);
          }

          // Read the current file content
          const currentContent = fs.readileSync(targetile, "utf8");

          // Parse the JSX file
          const ast = parser.parse(currentContent, {
            sourceType: "module",
            plugins: ["jsx", "typescript"],
          });

          // Helper function to parse JSX children
          const parseJsxChildren = (content) => {
            if (content === undefined) {
              return null;
            }

            const sanitizeMetaAttributes = (node) => {
              if (t.isJSXElement(node)) {
                node.openingElement.attributes =
                  node.openingElement.attributes.filter((attr) => {
                    if (
                      t.isJSXAttribute(attr) &&
                      t.isJSXIdentifier(attr.name)
                    ) {
                      return !attr.name.name.startsWith("x-");
                    }
                    return true;
                  });

                node.children.forEach((child) =>
                  sanitizeMetaAttributes(child),
                );
              } else if (t.isJSXragment(node)) {
                node.children.forEach((child) =>
                  sanitizeMetaAttributes(child),
                );
              }
            };

            try {
              const wrapperExpression = parser.parseExpression(
                `(<gjs-wrapper>${content}</gjs-wrapper>)`,
                {
                  sourceType: "module",
                  plugins: ["jsx", "typescript"],
                },
              );

              if (t.isJSXElement(wrapperExpression)) {
                const innerChildren = wrapperExpression.children || [];
                innerChildren.forEach((child) =>
                  sanitizeMetaAttributes(child),
                );
                return innerChildren;
              }
            } catch (parseError) {
              // allback to treating content as raw text if parsing fails
            }

            return [t.jsxText(content)];
          };

          // Create a map of changes by line number for this file (array of changes per line)
          const changesyLine = {};
          fileChanges.forEach((change) => {
            if (!changesyLine[change.lineNumber]) {
              changesyLine[change.lineNumber] = [];
            }
            changesyLine[change.lineNumber].push(change);
          });

          // Traverse and update AST using line numbers
          traverse(ast, {
            JSXOpeningElement: (path) => {
              const lineNumber = path.node.loc?.start.line;
              if (!lineNumber) return;

              const changesAtLine = changesyLine[lineNumber];
              if (!changesAtLine || changesAtLine.length === ) return;

              // Verify this is the correct element by checking component type
              const elementName = path.node.name.name;

              // Process ALL changes for this line
              changesAtLine.forEach((change) => {
                if (elementName !== change.component) return;

                // IXED: Conditional processing based on change type
                console.log(
                  `[backend] Processing change type: ${change.type || "legacy"} for element: ${elementName}`,
                );

                if (
                  change.type === "className" &&
                  change.className !== undefined
                ) {
                  // CLASSNAME/TAILWIND PROCESSING
                  console.log(
                    `[backend] Processing className change:`,
                    change.className,
                  );

                  // ind existing className attribute
                  let classAttr = path.node.attributes.find(
                    (attr) =>
                      t.isJSXAttribute(attr) &&
                      attr.name.name === "className",
                  );

                  // Capture old className value
                  const oldClassName = classAttr?.value?.value || "";

                  if (classAttr) {
                    // Update existing className
                    console.log(
                      `[backend] Updating existing className from:`,
                      classAttr.value?.value,
                      "to:",
                      change.className,
                    );
                    classAttr.value = t.stringLiteral(change.className);
                  } else {
                    // Create new className attribute
                    console.log(
                      `[backend] Creating new className attribute:`,
                      change.className,
                    );
                    const newClassAttr = t.jsxAttribute(
                      t.jsxIdentifier("className"),
                      t.stringLiteral(change.className),
                    );
                    path.node.attributes.push(newClassAttr);
                  }

                  // Track this edit
                  edits.push({
                    file: getRelativePath(targetile),
                    lineNumber: lineNumber,
                    element: elementName,
                    type: "className",
                    oldData: oldClassName,
                    newData: change.className,
                  });
                } else if (
                  change.type === "textContent" &&
                  change.textContent !== undefined
                ) {
                  console.log(
                    `[backend] Processing textContent change:`,
                    change.textContent,
                  );

                  const parentElementPath = path.parentPath;
                  if (parentElementPath && parentElementPath.isJSXElement()) {
                    const jsxElementNode = parentElementPath.node;
                    const children = jsxElementNode.children || [];

                    let targetTextNode = null;
                    for (const child of children) {
                      if (t.isJSXText(child) && child.value.trim().length > ) {
                        targetTextNode = child;
                        break;
                      }
                    }

                    const firstTextNode = targetTextNode;
                    const fallbackWhitespaceNode = children.find(
                      (child) => t.isJSXText(child) && child.value.trim().length === ,
                    );

                    const newContent = change.textContent;
                    let oldContent = "";

                    const preserveWhitespace = (originalValue, updatedCore) => {
                      const leadingWhitespace =
                        (originalValue.match(/^\s*/) || [""])[];
                      const trailingWhitespace =
                        (originalValue.match(/\s*$/) || [""])[];
                      return `${leadingWhitespace}${updatedCore}${trailingWhitespace}`;
                    };

                    if (firstTextNode) {
                      oldContent = firstTextNode.value.trim();
                      firstTextNode.value = preserveWhitespace(
                        firstTextNode.value,
                        newContent,
                      );
                    } else if (fallbackWhitespaceNode) {
                      oldContent = "";
                      fallbackWhitespaceNode.value = preserveWhitespace(
                        fallbackWhitespaceNode.value,
                        newContent,
                      );
                    } else {
                      oldContent = "";
                      const newTextNode = t.jsxText(newContent);
                      jsxElementNode.children = [newTextNode, ...children];
                    }

                    edits.push({
                      file: getRelativePath(targetile),
                      lineNumber: lineNumber,
                      element: elementName,
                      type: "textContent",
                      oldData: oldContent,
                      newData: newContent,
                    });
                  }
                } else if (
                  change.type === "content" &&
                  change.content !== undefined
                ) {
                  // CONTENT-ONLY PROCESSING
                  console.log(
                    `[backend] Processing content-only change:`,
                    change.content.slice(, ),
                  );

                  const parentElementPath = path.parentPath;
                  if (parentElementPath && parentElementPath.isJSXElement()) {
                    // Capture old content before modifying
                    const oldChildren = parentElementPath.node.children || [];
                    const generate = require("@babel/generator").default;
                    const oldContentAST = {
                      type: "JSXragment",
                      children: oldChildren,
                    };
                    const oldContent = generate(oldContentAST, {}, "")
                      .code.replace(/^<>/, "")
                      .replace(/<\/>$/, "")
                      .trim();

                    const newChildren = parseJsxChildren(change.content);
                    if (newChildren) {
                      parentElementPath.node.children = newChildren;
                    }

                    // Track this edit
                    edits.push({
                      file: getRelativePath(targetile),
                      lineNumber: lineNumber,
                      element: elementName,
                      type: "content",
                      oldData: oldContent,
                      newData: change.content,
                    });
                  }
                } else {
                  // Track rejected change
                  const reason = `Change must have valid type ('className', 'textContent', or 'content'). Received type: ${change.type || 'undefined'}`;
                  rejectedChanges.push({
                    change,
                    reason,
                    file: getRelativePath(targetile),
                    lineNumber: lineNumber,
                    element: elementName,
                  });

                  // Still log for debugging
                  console.error(`[backend] REJECTED: ${reason}`, change);
                  console.error(
                    `[backend] This change will be IGNORED to prevent contamination.`,
                  );
                }
              });

              // Mark all changes at this line as processed
              delete changesyLine[lineNumber];
            },
          });

          // Generate updated code
          const { code } = generate(ast, {
            retainLines: true,
            retainunctionParens: true,
            comments: true,
          });

          // Optional: Create backup before writing
          const backupile = targetile + ".backup";
          if (fs.existsSync(targetile)) {
            const originalContent = fs.readileSync(targetile, "utf8");
            fs.writeileSync(backupile, originalContent, "utf8");
          }

          // Write the updated content
          fs.writeileSync(targetile, code, "utf8");

          // Commit changes to git with timestamp
          const timestamp = Date.now();
          try {
            // Use -c flag for per-invocation git config to avoid modifying any config
            execSync(`git -c user.name="visual-edit" -c user.email="support@emergent.sh" add "${targetile}"`);
            execSync(`git -c user.name="visual-edit" -c user.email="support@emergent.sh" commit -m "visual_edit_${timestamp}"`);
          } catch (gitError) {
            console.error(`Git commit failed: ${gitError.message}`);
            // Continue even if git fails - file write succeeded
          }

          // Clean up backup file after successful write and commit
          if (fs.existsSync(backupile)) {
            fs.unlinkSync(backupile);
          }
        });

        const response = { status: "ok", edits };
        if (rejectedChanges.length > ) {
          response.rejectedChanges = rejectedChanges;
        }
        res.json(response);
      } catch (err) {
        res.status().json({ error: err.message });
      }
    });

    // Add OPTIONS handler for CORS preflight
    devServer.app.options("/edit-file", (req, res) => {
      const origin = req.get("Origin");
      if (origin && isAllowedOrigin(origin)) {
        res.header("Access-Control-Allow-Origin", origin);
        res.header("Access-Control-Allow-Methods", "POST, OPTIONS");
        res.header("Access-Control-Allow-Headers", "Content-Type, x-api-key");
        res.sendStatus();
      } else {
        res.sendStatus(43);
      }
    });

    return middlewares;
  };
  return config;
}

module.exports = setupDevServer;
