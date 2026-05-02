import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, FileText, Search, Trash2, ArrowLeft, RefreshCw,
  Database, Filter, X, CheckCircle, AlertCircle, Loader2,
  FolderOpen, Tag, Package, FileUp
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const KnowledgeBase = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const bulkFileInputRef = useRef(null);
  
  // State
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [querying, setQuerying] = useState(false);
  
  // Query state
  const [queryText, setQueryText] = useState('');
  const [queryResults, setQueryResults] = useState(null);
  const [filterProduct, setFilterProduct] = useState('');
  const [filterType, setFilterType] = useState('');
  
  // Upload form state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadDocType, setUploadDocType] = useState('foundation');
  const [uploadProducts, setUploadProducts] = useState('all');
  const [uploadVersion, setUploadVersion] = useState('1.0');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(null);

  const getToken = () => localStorage.getItem('token');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = getToken();
      const headers = { 'Authorization': `Bearer ${token}` };
      
      const [docsRes, statsRes] = await Promise.all([
        fetch(`${API_URL}/api/knowledge-base/documents`, { headers }),
        fetch(`${API_URL}/api/knowledge-base/stats`, { headers })
      ]);
      
      if (docsRes.ok) setDocuments(await docsRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
    } catch (err) {
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e, isBulk = false) => {
    const files = Array.from(e.target.files);
    const mdFiles = files.filter(f => f.name.endsWith('.md'));
    
    if (mdFiles.length !== files.length) {
      alert('Only markdown (.md) files are supported');
    }
    
    if (mdFiles.length > 0) {
      setSelectedFiles(mdFiles);
      setShowUploadModal(true);
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;
    
    setUploading(true);
    setUploadProgress({ current: 0, total: selectedFiles.length, results: [] });
    
    const token = getToken();
    const isBulk = selectedFiles.length > 1;
    
    try {
      if (isBulk) {
        // Bulk upload
        const formData = new FormData();
        selectedFiles.forEach(file => formData.append('files', file));
        formData.append('doc_type', uploadDocType);
        formData.append('products', uploadProducts);
        formData.append('version', uploadVersion);
        
        const response = await fetch(`${API_URL}/api/knowledge-base/upload-bulk`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        });
        
        if (response.ok) {
          const result = await response.json();
          setUploadProgress({
            current: selectedFiles.length,
            total: selectedFiles.length,
            results: result.results,
            errors: result.errors
          });
        }
      } else {
        // Single file upload
        const formData = new FormData();
        formData.append('file', selectedFiles[0]);
        formData.append('doc_type', uploadDocType);
        formData.append('products', uploadProducts);
        formData.append('version', uploadVersion);
        
        const response = await fetch(`${API_URL}/api/knowledge-base/upload`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        });
        
        if (response.ok) {
          const result = await response.json();
          setUploadProgress({
            current: 1,
            total: 1,
            results: [result],
            errors: []
          });
        }
      }
      
      // Refresh data after upload
      await fetchData();
      
      // Reset after delay
      setTimeout(() => {
        setShowUploadModal(false);
        setSelectedFiles([]);
        setUploadProgress(null);
      }, 2000);
      
    } catch (err) {
      alert('Upload failed: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!queryText.trim()) return;
    
    setQuerying(true);
    try {
      const token = getToken();
      const response = await fetch(`${API_URL}/api/knowledge-base/query`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: queryText,
          top_k: 5,
          filter_by_product: filterProduct || null,
          filter_by_type: filterType || null,
          min_score: 0.4
        })
      });
      
      if (response.ok) {
        setQueryResults(await response.json());
      }
    } catch (err) {
      console.error('Query error:', err);
    } finally {
      setQuerying(false);
    }
  };

  const handleDelete = async (docId) => {
    if (!confirm('Delete this document? This cannot be undone.')) return;
    
    try {
      const token = getToken();
      await fetch(`${API_URL}/api/knowledge-base/documents/${docId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      await fetchData();
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  const getTypeColor = (type) => {
    const colors = {
      foundation: 'bg-purple-100 text-purple-700',
      product: 'bg-blue-100 text-blue-700',
      operations: 'bg-green-100 text-green-700',
      technical: 'bg-yellow-100 text-yellow-700',
      training: 'bg-pink-100 text-pink-700'
    };
    return colors[type] || 'bg-gray-100 text-gray-700';
  };

  const getProductColor = (product) => {
    const colors = {
      all: 'bg-gray-100 text-gray-700',
      urgaa: 'bg-orange-100 text-orange-700',
      gstsaas: 'bg-emerald-100 text-emerald-700',
      ignition: 'bg-red-100 text-red-700',
      arjun: 'bg-indigo-100 text-indigo-700'
    };
    return colors[product] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-40" style={{ borderTopColor: '#F47216', borderTopWidth: '3px' }}>
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/kailash')} className="p-2 hover:bg-gray-100 rounded-lg">
              <ArrowLeft size={20} className="text-gray-600" />
            </button>
            <div>
              <h1 className="text-xl font-bold flex items-center gap-2" style={{ color: '#0A3D62' }}>
                <Database size={24} />
                Knowledge Base
              </h1>
              <p className="text-sm text-gray-500">RAG-powered document retrieval for all AI agents</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <button onClick={fetchData} className="p-2 hover:bg-gray-100 rounded-lg" title="Refresh">
              <RefreshCw size={20} className="text-gray-600" />
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => handleFileSelect(e, false)}
              accept=".md"
              className="hidden"
            />
            <input
              type="file"
              ref={bulkFileInputRef}
              onChange={(e) => handleFileSelect(e, true)}
              accept=".md"
              multiple
              className="hidden"
            />
            <button
              onClick={() => bulkFileInputRef.current?.click()}
              className="px-4 py-2 text-white rounded-lg font-medium flex items-center gap-2 hover:opacity-90"
              style={{ background: '#F47216' }}
            >
              <Upload size={18} />
              Upload Documents
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <Database size={18} style={{ color: '#0A3D62' }} />
                <span className="text-sm text-gray-500">Total Vectors</span>
              </div>
              <div className="text-2xl font-bold" style={{ color: '#0A3D62' }}>{stats.total_vectors?.toLocaleString() || 0}</div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <FileText size={18} style={{ color: '#F47216' }} />
                <span className="text-sm text-gray-500">Documents</span>
              </div>
              <div className="text-2xl font-bold" style={{ color: '#0A3D62' }}>{stats.total_documents || 0}</div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <Tag size={18} className="text-purple-500" />
                <span className="text-sm text-gray-500">By Type</span>
              </div>
              <div className="text-sm text-gray-600">
                {stats.by_doc_type && Object.entries(stats.by_doc_type).map(([k, v]) => (
                  <span key={k} className="mr-2">{k}: {v}</span>
                ))}
              </div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <Package size={18} className="text-blue-500" />
                <span className="text-sm text-gray-500">By Product</span>
              </div>
              <div className="text-sm text-gray-600">
                {stats.by_product && Object.entries(stats.by_product).map(([k, v]) => (
                  <span key={k} className="mr-2">{k}: {v}</span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Search Section */}
        <div className="bg-white rounded-lg p-6 border border-gray-200 mb-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: '#0A3D62' }}>
            <Search size={20} />
            Query Knowledge Base
          </h2>
          
          <form onSubmit={handleQuery} className="space-y-4">
            <div className="flex gap-3">
              <input
                type="text"
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                placeholder="Ask a question about your documents..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="submit"
                disabled={querying || !queryText.trim()}
                className="px-6 py-3 text-white rounded-lg font-medium flex items-center gap-2 disabled:opacity-50"
                style={{ background: '#0A3D62' }}
              >
                {querying ? <Loader2 size={18} className="animate-spin" /> : <Search size={18} />}
                Search
              </button>
            </div>
            
            <div className="flex gap-3 items-center">
              <Filter size={16} className="text-gray-400" />
              <select
                value={filterProduct}
                onChange={(e) => setFilterProduct(e.target.value)}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm"
              >
                <option value="">All Products</option>
                <option value="urgaa">URGAA</option>
                <option value="gstsaas">GSTSAAS</option>
                <option value="ignition">IGNITION</option>
                <option value="arjun">ARJUN</option>
              </select>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm"
              >
                <option value="">All Types</option>
                <option value="foundation">Foundation</option>
                <option value="product">Product</option>
                <option value="operations">Operations</option>
                <option value="technical">Technical</option>
                <option value="training">Training</option>
              </select>
            </div>
          </form>

          {/* Query Results */}
          {queryResults && (
            <div className="mt-6 border-t border-gray-200 pt-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-700">
                  Found {queryResults.total_results} relevant sources
                </h3>
                <button onClick={() => setQueryResults(null)} className="text-gray-400 hover:text-gray-600">
                  <X size={18} />
                </button>
              </div>
              
              {queryResults.sources.length > 0 ? (
                <div className="space-y-4">
                  {queryResults.sources.map((source, idx) => (
                    <div key={idx} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText size={16} style={{ color: '#F47216' }} />
                        <span className="font-medium text-gray-900">{source.source_filename}</span>
                        <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                          {Math.round(source.relevance_score * 100)}% match
                        </span>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${getTypeColor(source.doc_type)}`}>
                          {source.doc_type}
                        </span>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${getProductColor(source.products)}`}>
                          {source.products}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 whitespace-pre-wrap">{source.chunk_text}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No relevant documents found. Try adjusting your query or filters.</p>
              )}
            </div>
          )}
        </div>

        {/* Documents List */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold flex items-center gap-2" style={{ color: '#0A3D62' }}>
              <FolderOpen size={20} />
              Uploaded Documents ({documents.length})
            </h2>
          </div>
          
          {loading ? (
            <div className="p-8 text-center text-gray-500">
              <Loader2 size={24} className="animate-spin mx-auto mb-2" />
              Loading documents...
            </div>
          ) : documents.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <FileText size={48} className="mx-auto mb-4 text-gray-300" />
              <p>No documents uploaded yet.</p>
              <p className="text-sm">Click "Upload Documents" to add your first document.</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {documents.map((doc) => (
                <div key={doc.doc_id} className="p-4 hover:bg-gray-50 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <FileText size={24} className="text-gray-400" />
                    <div>
                      <h3 className="font-medium text-gray-900">{doc.filename}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`px-2 py-0.5 text-xs rounded-full ${getTypeColor(doc.doc_type)}`}>
                          {doc.doc_type}
                        </span>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${getProductColor(doc.products)}`}>
                          {doc.products}
                        </span>
                        <span className="text-xs text-gray-400">v{doc.version}</span>
                        <span className="text-xs text-gray-400">{doc.total_chunks} chunks</span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(doc.doc_id)}
                    className="p-2 hover:bg-red-50 rounded-lg text-red-500"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full">
            <div className="p-4 border-b border-gray-200 flex justify-between items-center" style={{ background: '#0A3D62' }}>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <FileUp size={20} />
                Upload Documents ({selectedFiles.length} files)
              </h2>
              <button onClick={() => { setShowUploadModal(false); setSelectedFiles([]); setUploadProgress(null); }} className="p-1 hover:bg-white/10 rounded-lg">
                <X size={20} className="text-white" />
              </button>
            </div>
            
            <div className="p-6">
              {uploadProgress ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    {uploadProgress.current === uploadProgress.total ? (
                      <CheckCircle size={24} className="text-green-500" />
                    ) : (
                      <Loader2 size={24} className="text-blue-500 animate-spin" />
                    )}
                    <span className="font-medium">
                      {uploadProgress.current === uploadProgress.total 
                        ? 'Upload Complete!' 
                        : `Uploading... ${uploadProgress.current}/${uploadProgress.total}`}
                    </span>
                  </div>
                  
                  {uploadProgress.results?.length > 0 && (
                    <div className="bg-green-50 rounded-lg p-3">
                      <p className="text-green-700 font-medium">{uploadProgress.results.length} documents uploaded successfully</p>
                    </div>
                  )}
                  
                  {uploadProgress.errors?.length > 0 && (
                    <div className="bg-red-50 rounded-lg p-3">
                      <p className="text-red-700 font-medium">{uploadProgress.errors.length} failed:</p>
                      {uploadProgress.errors.map((err, i) => (
                        <p key={i} className="text-red-600 text-sm">{err.filename}: {err.error}</p>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="font-medium text-gray-700 mb-2">Selected Files:</p>
                    <ul className="text-sm text-gray-600 space-y-1 max-h-32 overflow-y-auto">
                      {selectedFiles.map((file, i) => (
                        <li key={i} className="flex items-center gap-2">
                          <FileText size={14} />
                          {file.name}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Document Type</label>
                      <select
                        value={uploadDocType}
                        onChange={(e) => setUploadDocType(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      >
                        <option value="foundation">Foundation</option>
                        <option value="product">Product</option>
                        <option value="operations">Operations</option>
                        <option value="technical">Technical</option>
                        <option value="training">Training</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Product</label>
                      <select
                        value={uploadProducts}
                        onChange={(e) => setUploadProducts(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      >
                        <option value="all">All Products</option>
                        <option value="urgaa">URGAA</option>
                        <option value="gstsaas">GSTSAAS</option>
                        <option value="ignition">IGNITION</option>
                        <option value="arjun">ARJUN</option>
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Version</label>
                    <input
                      type="text"
                      value={uploadVersion}
                      onChange={(e) => setUploadVersion(e.target.value)}
                      placeholder="1.0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  
                  <div className="flex gap-3 pt-4">
                    <button
                      onClick={() => { setShowUploadModal(false); setSelectedFiles([]); }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleUpload}
                      disabled={uploading}
                      className="flex-1 px-4 py-2 text-white rounded-lg hover:opacity-90 flex items-center justify-center gap-2"
                      style={{ background: '#F47216' }}
                    >
                      {uploading ? <Loader2 size={18} className="animate-spin" /> : <Upload size={18} />}
                      Upload
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeBase;
