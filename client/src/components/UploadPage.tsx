import { useState, useRef } from 'react';
import { uploadAd } from '../api/endpoints';

export default function UploadPage() {
  const [title, setTitle] = useState('');
  const [brand, setBrand] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('general');
  const [tags, setTags] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const categories = [
    'general', 'tech', 'sports', 'food', 'auto', 'entertainment',
    'travel', 'beauty', 'toys', 'gaming', 'fashion', 'health',
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      if (f.type.startsWith('image/')) {
        setPreview(URL.createObjectURL(f));
      } else {
        setPreview(null);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title || !brand) {
      setError('Please fill in all required fields and select a file.');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(false);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title);
      formData.append('brand', brand);
      if (description) formData.append('description', description);
      formData.append('category', category);
      if (tags) formData.append('tags', tags);

      await uploadAd(formData);
      setSuccess(true);
      setTitle('');
      setBrand('');
      setDescription('');
      setCategory('general');
      setTags('');
      setFile(null);
      setPreview(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto bg-dark">
      <div className="max-w-lg mx-auto p-4 pt-12 pb-20">
        <h1 className="text-2xl font-bold mb-6">Upload an Ad</h1>

        {success && (
          <div className="mb-4 p-4 bg-green-500/20 border border-green-500 rounded-xl text-green-400">
            Ad uploaded successfully!
          </div>
        )}

        {error && (
          <div className="mb-4 p-4 bg-red-500/20 border border-red-500 rounded-xl text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* File Upload */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Media File *</label>
            <input
              ref={fileInputRef}
              type="file"
              accept="video/mp4,video/webm,video/mov,image/jpeg,image/png,image/gif,image/webp"
              onChange={handleFileChange}
              className="w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:opacity-90"
            />
            {preview && (
              <img src={preview} alt="Preview" className="mt-2 rounded-lg max-h-48 object-cover" />
            )}
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Title *</label>
            <input
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="e.g., New Nike Air Max"
              className="w-full px-4 py-3 bg-surface text-white rounded-xl outline-none focus:ring-2 focus:ring-primary placeholder-gray-500"
            />
          </div>

          {/* Brand */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Brand *</label>
            <input
              type="text"
              value={brand}
              onChange={e => setBrand(e.target.value)}
              placeholder="e.g., Nike"
              className="w-full px-4 py-3 bg-surface text-white rounded-xl outline-none focus:ring-2 focus:ring-primary placeholder-gray-500"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Description</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="Describe the ad..."
              rows={3}
              className="w-full px-4 py-3 bg-surface text-white rounded-xl outline-none focus:ring-2 focus:ring-primary placeholder-gray-500 resize-none"
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Category</label>
            <select
              value={category}
              onChange={e => setCategory(e.target.value)}
              className="w-full px-4 py-3 bg-surface text-white rounded-xl outline-none focus:ring-2 focus:ring-primary"
            >
              {categories.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Tags (comma-separated)</label>
            <input
              type="text"
              value={tags}
              onChange={e => setTags(e.target.value)}
              placeholder="e.g., nike,shoes,sports"
              className="w-full px-4 py-3 bg-surface text-white rounded-xl outline-none focus:ring-2 focus:ring-primary placeholder-gray-500"
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={uploading}
            className="w-full py-3 bg-primary text-white rounded-full font-semibold hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            {uploading ? 'Uploading...' : 'Upload Ad'}
          </button>
        </form>
      </div>
    </div>
  );
}