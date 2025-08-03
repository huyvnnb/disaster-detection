import React, { useState } from 'react';
import axios from 'axios';
import ImageViewer from './components/ImageViewer';
import ObjectList from './components/ObjectList';
import { Spinner } from './components/Spinner';

const MODERN_COLORS = [
  '#3B82F6',
  '#10B981',
  '#F97316',
  '#8B5CF6',
  '#EF4444',
  '#06B6D4',
  '#FBBF24',
  '#6366F1',
  '#EC4899',
  '#22C55E',
];

const getColorForIndex = (index) => {
  return MODERN_COLORS[index % MODERN_COLORS.length];
};

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [bounds, setBounds] = useState([]);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [hoveredId, setHoveredId] = useState(null); // State cho hiệu ứng hover

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setBounds([]);
      setSelectedIds(new Set());
      setError('');
    }
  };

  const handlePredict = async () => {
    if (!file) return;
    setIsLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const API_URL = 'http://127.0.0.1:8000/yolo/predict';
      const response = await axios.post(API_URL, formData);

      if (response.data.success) {
        const processedBounds = response.data.data.map((b, index) => ({
          ...b,
          id: index,
          color: getColorForIndex(b.class_id),
        }));
        setBounds(processedBounds);
        setSelectedIds(new Set(processedBounds.map(b => b.id)));
      } else {
        setError(response.data.message || 'API trả về lỗi.');
      }
    } catch (err) {
      setError('Lỗi kết nối. Backend FastAPI đã chạy chưa?');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleBound = (id) => {
    setSelectedIds(prev => {
      const newIds = new Set(prev);
      newIds.has(id) ? newIds.delete(id) : newIds.add(id);
      return newIds;
    });
  };

  const handleSelectAll = (isChecked) => {
    setSelectedIds(isChecked ? new Set(bounds.map(b => b.id)) : new Set());
  };

  const handleMouseEnter = (id) => setHoveredId(id);
  const handleMouseLeave = () => setHoveredId(null);

  const selectedBoundsToDraw = bounds.filter(b => selectedIds.has(b.id));

  return (
    <div className="flex flex-col md:flex-row h-screen bg-gray-100 text-gray-800 font-sans">
      {/* Cột Trái */}
      <div className="flex-grow flex flex-col items-center justify-center p-4 bg-gray-200">
        {previewUrl ? (
          <ImageViewer
            imageUrl={previewUrl}
            bounds={selectedBoundsToDraw}
            hoveredId={hoveredId}
          />
        ) : (
          <div className="text-center p-8 border-2 border-dashed border-gray-400 rounded-xl">
            <h2 className="text-2xl font-bold text-gray-700 mb-4">Trình diễn YOLO</h2>
            <p className="text-gray-500 mb-6">Hãy chọn một ảnh để bắt đầu</p>
          </div>
        )}
      </div>

      {/* Cột Phải */}
      <div className="w-full md:w-[380px] flex-shrink-0 bg-white p-6 flex flex-col border-l border-gray-200">
        <div className="mb-6">
          <label className="w-full text-center block bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-4 rounded-lg cursor-pointer transition-colors">
            <span>{file ? `Đã chọn: ${file.name}` : 'Tải ảnh lên'}</span>
            <input type="file" onChange={handleFileChange} accept="image/*" className="hidden" />
          </label>
        </div>
        {file && (
          <div className="mb-6">
            <button
              onClick={handlePredict}
              disabled={isLoading}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? <Spinner /> : 'Phân tích ảnh'}
            </button>
          </div>
        )}
        {error && <p className="text-red-700 bg-red-100 border border-red-300 p-3 rounded-lg mb-4 font-medium">{error}</p>}
        <div className="flex-grow overflow-y-auto">
          <ObjectList
            bounds={bounds}
            selectedIds={selectedIds}
            onToggle={handleToggleBound}
            onSelectAll={handleSelectAll}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
          />
        </div>
      </div>
    </div>
  );
}

export default App;