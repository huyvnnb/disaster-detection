import React from 'react';

const ObjectListItem = ({ bound, isSelected, onToggle, onMouseEnter, onMouseLeave }) => (
  <li
    className="flex items-center p-2.5 hover:bg-gray-100 rounded-md cursor-pointer transition-colors"
    onClick={() => onToggle(bound.id)}
    onMouseEnter={() => onMouseEnter(bound.id)}
    onMouseLeave={onMouseLeave}
  >
    <input
      type="checkbox"
      checked={isSelected}
      readOnly
      className="mr-3 h-4 w-4 rounded text-blue-600 border-gray-300 focus:ring-blue-500"
    />
    <div
      className="w-4 h-4 rounded-sm mr-3 flex-shrink-0"
      style={{ backgroundColor: bound.color }}
    ></div>
    <span className="flex-grow font-medium text-gray-800 capitalize truncate">{bound.class_name}</span>
    <span className="text-sm font-semibold text-gray-600 ml-2">{`${Math.round(bound.confidence * 100)}%`}</span>
  </li>
);

const ObjectList = ({ bounds, selectedIds, onToggle, onSelectAll, onMouseEnter, onMouseLeave }) => {
  if (bounds.length === 0) {
    return <p className="text-gray-500 text-center mt-10">Chọn ảnh và nhấn "Phân tích" để xem kết quả.</p>;
  }

  const allSelected = selectedIds.size === bounds.length;

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-xl font-bold mb-4 text-gray-900">Đối tượng phát hiện ({bounds.length})</h2>
      <div
        className="flex items-center p-2 border-b border-gray-200 mb-2 cursor-pointer"
        onClick={() => onSelectAll(!allSelected)}
        onMouseEnter={() => onMouseEnter(null)} // Đảm bảo không có box nào được highlight khi hover vào khu vực này
      >
        <input
          type="checkbox"
          checked={allSelected}
          readOnly
          className="mr-3 h-4 w-4 rounded text-blue-600 border-gray-300"
        />
        <label className="font-bold text-gray-700 cursor-pointer select-none">Chọn tất cả</label>
      </div>
      <ul className="space-y-1 overflow-y-auto flex-grow">
        {bounds.map(bound => (
          <ObjectListItem
            key={bound.id}
            bound={bound}
            isSelected={selectedIds.has(bound.id)}
            onToggle={onToggle}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
          />
        ))}
      </ul>
    </div>
  );
};

export default ObjectList;