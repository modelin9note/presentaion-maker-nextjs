'use client';

import { usePresentationStore, Slide } from '@/store/usePresentationStore';
import { useState } from 'react';
import { Loader2, Download, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';

export default function GenerateStep() {
    const {
        apiKey, slides, setSlides, isLoading, setIsLoading,
        fileName, setFileName, setCurrentStep
    } = usePresentationStore();

    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState('');
    const [error, setError] = useState('');
    const [isDone, setIsDone] = useState(false);

    const generateImages = async () => {
        setIsLoading(true);
        setError('');
        setIsDone(false);
        setProgress(0);

        try {
            const newSlides = [...slides];
            let completed = 0;

            // Generate images sequentially to avoid rate limits
            for (let i = 0; i < newSlides.length; i++) {
                const slide = newSlides[i];
                if (slide.image_prompt && !slide.image_base64) {
                    setStatus(`Generating image for Slide ${slide.id}...`);

                    const response = await fetch('/api/generate/image', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            api_key: apiKey,
                            prompt: slide.image_prompt,
                            model: 'imagen-4.0-generate-001'
                        })
                    });

                    const contentType = response.headers.get("content-type");
                    if (!contentType || !contentType.includes("application/json")) {
                        throw new Error("API not found. Make sure you are running 'vercel dev'.");
                    }

                    const data = await response.json();
                    if (data.image_base64) {
                        newSlides[i].image_base64 = data.image_base64;
                    } else {
                        console.error(`Failed to generate image for slide ${slide.id}: ${data.error}`);
                    }
                }
                completed++;
                setProgress((completed / newSlides.length) * 50); // First 50% is image gen
            }

            setSlides(newSlides);
            await generatePPT(newSlides);

        } catch (err: any) {
            setError(err.message);
            setIsLoading(false);
        }
    };

    const generatePPT = async (currentSlides: Slide[]) => {
        setStatus('Assembling PowerPoint...');
        try {
            const response = await fetch('/api/generate/ppt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ slides: currentSlides })
            });

            if (!response.ok) throw new Error('Failed to generate PPT');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${fileName || 'presentation'}.pptx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            setProgress(100);
            setStatus('Done!');
            setIsDone(true);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">Generate Presentation</h2>

            {!isLoading && !isDone && (
                <div className="max-w-md mx-auto mb-8 text-left">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Output Filename</label>
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={fileName}
                            onChange={(e) => setFileName(e.target.value)}
                            className="flex-1 p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            placeholder="MyPresentation"
                        />
                        <span className="self-center text-gray-500">.pptx</span>
                    </div>
                </div>
            )}

            {error && (
                <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 flex items-center gap-2 justify-center">
                    <AlertCircle size={18} /> {error}
                </div>
            )}

            <div className="py-8">
                {isLoading ? (
                    <div className="space-y-4">
                        <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto" />
                        <p className="text-gray-600">{status}</p>
                        <div className="w-full bg-gray-200 rounded-full h-2.5 max-w-md mx-auto">
                            <div className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
                        </div>
                    </div>
                ) : isDone ? (
                    <div className="space-y-6">
                        <div className="flex flex-col items-center gap-2 text-green-600">
                            <CheckCircle size={48} />
                            <p className="text-xl font-medium">Generation Complete!</p>
                        </div>
                        <p className="text-gray-600">Your presentation has been downloaded.</p>
                        <button
                            onClick={() => setCurrentStep(1)}
                            className="bg-gray-100 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors flex items-center gap-2 mx-auto"
                        >
                            <RefreshCw size={18} /> Start New Project
                        </button>
                    </div>
                ) : (
                    <button
                        onClick={generateImages}
                        className="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2 mx-auto"
                    >
                        <Download size={18} /> Start Generation
                    </button>
                )}
            </div>
        </div>
    );
}
