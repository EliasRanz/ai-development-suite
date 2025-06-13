import React, { useState } from 'react';
import { X, Save, Palette } from 'lucide-react';

interface FeatureModalProps {
  onSave: (featureData: {
    name: string;
    description: string;
    color: string;
  }) => void;
  onClose: () => void;
}

const FEATURE_COLORS = [
  '#3B82F6', // Blue
  '#10B981', // Green
  '#F59E0B', // Yellow
  '#EF4444', // Red
  '#8B5CF6', // Purple
  '#06B6D4', // Cyan
  '#F97316', // Orange
  '#84CC16', // Lime
];

export default function FeatureModal({ onSave, onClose }: FeatureModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [selectedColor, setSelectedColor] = useState(FEATURE_COLORS[0]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    onSave({
      name: name.trim(),
      description: description.trim(),
      color: selectedColor,
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-900">
            Create New Feature
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Feature Name *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Enter feature name"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Enter feature description"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Palette className="w-4 h-4 inline mr-1" />
              Color Theme
            </label>
            <div className="grid grid-cols-4 gap-2">
              {FEATURE_COLORS.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setSelectedColor(color)}
                  className={`w-12 h-12 rounded-lg border-2 transition-all ${
                    selectedColor === color
                      ? 'border-gray-900 scale-110'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  style={{ backgroundColor: color }}
                >
                  {selectedColor === color && (
                    <div className="w-full h-full rounded-md bg-white bg-opacity-30 flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!name.trim()}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Save className="w-4 h-4" />
              <span>Create Feature</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
