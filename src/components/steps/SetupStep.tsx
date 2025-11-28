'use client';

import { usePresentationStore } from '@/store/usePresentationStore';
import { useState } from 'react';
import { Upload, ArrowRight } from 'lucide-react';

export default function SetupStep() {
    const {
        apiKey, setApiKey,
        topic, setTopic,
        language, setLanguage,
        slideCount, setSlideCount,
        setCurrentStep,
        materials, setMaterials
    } = usePresentationStore();

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files) {
            Array.from(files).forEach(file => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const text = e.target?.result as string;
                    setMaterials(materials + '\n\n' + text);
                };
                reader.readAsText(file);
            });
        }
    };

    const handleNext = () => {
        if (!apiKey || !topic) return;
        setCurrentStep(2);
    };

    return (
        <div className="space-y-6 bg-white p-8 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-2xl font-semibold text-gray-800">Project Setup</h2>

            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Gemini API Key</label>
                    <input
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="Enter your Google Gemini API Key"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Presentation Topic</label>
                    <input
                        type="text"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="e.g., The Future of Artificial Intelligence"
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
                        <select
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                            className="w-full p-2 border rounded-lg outline-none"
                        >
                            <option value="Korean">Korean</option>
                            <option value="English">English</option>
                            <option value="Mixed (Korean/English)">Mixed</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Slide Count: {slideCount}</label>
                        <input
                            type="range"
                            min="1"
                            max="50"
                            value={slideCount}
                            onChange={(e) => setSlideCount(parseInt(e.target.value))}
                            className="w-full"
                        />
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Reference Materials</label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:bg-gray-50 transition-colors cursor-pointer relative">
                        <input
                            type="file"
                            multiple
                            accept=".txt,.md"
                            onChange={handleFileUpload}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        />
                        <Upload className="mx-auto h-10 w-10 text-gray-400 mb-2" />
                        <p className="text-sm text-gray-500">Drop text files here or click to upload</p>
                    </div>
                    <textarea
                        value={materials}
                        onChange={(e) => setMaterials(e.target.value)}
                        className="w-full mt-2 p-2 border rounded-lg h-32 text-sm"
                        placeholder="Or paste content here..."
                    />
                </div>
            </div>

            <button
                onClick={handleNext}
                disabled={!apiKey || !topic}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
                Create Project <ArrowRight size={18} />
            </button>
        </div>
    );
}
