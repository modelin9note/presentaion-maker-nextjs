'use client';

import { usePresentationStore } from '@/store/usePresentationStore';
import { useState } from 'react';
import { Loader2, ArrowRight, AlertCircle } from 'lucide-react';

export default function DraftStep() {
    const {
        apiKey, topic, language, slideCount, materials,
        setSlides, setCurrentStep, isLoading, setIsLoading
    } = usePresentationStore();

    const [error, setError] = useState('');

    const generateDraft = async () => {
        setIsLoading(true);
        setError('');

        try {
            const response = await fetch('/api/generate/draft', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    api_key: apiKey,
                    topic,
                    materials,
                    language,
                    slide_count: slideCount
                })
            });

            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                const text = await response.text();
                console.error("API Error (Non-JSON response):", text);
                throw new Error("API not found or returned invalid data. Are you running 'vercel dev'?");
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate draft');
            }

            if (data.slides) {
                setSlides(data.slides);
                setCurrentStep(3);
            } else {
                throw new Error('Invalid response format');
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">AI Draft Generation</h2>

            <div className="bg-blue-50 p-4 rounded-lg mb-6 text-left">
                <p className="text-sm text-blue-800">
                    <strong>Topic:</strong> {topic}<br />
                    <strong>Language:</strong> {language}<br />
                    <strong>Slides:</strong> {slideCount}
                </p>
            </div>

            {error && (
                <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 flex items-center gap-2 justify-center">
                    <AlertCircle size={18} /> {error}
                </div>
            )}

            <div className="py-8">
                {isLoading ? (
                    <div className="flex flex-col items-center gap-4">
                        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
                        <p className="text-gray-600">Analyzing materials and structuring your presentation...</p>
                    </div>
                ) : (
                    <button
                        onClick={generateDraft}
                        className="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2 mx-auto"
                    >
                        Generate Draft <ArrowRight size={18} />
                    </button>
                )}
            </div>

            <button
                onClick={() => setCurrentStep(1)}
                className="text-gray-500 hover:text-gray-700 text-sm mt-4"
                disabled={isLoading}
            >
                Back to Setup
            </button>
        </div>
    );
}
