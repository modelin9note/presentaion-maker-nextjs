'use client';

import { usePresentationStore, Slide } from '@/store/usePresentationStore';
import { useState } from 'react';
import { ChevronDown, ChevronUp, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function EditStep() {
    const { slides, setSlides, setCurrentStep } = usePresentationStore();
    const [expandedSlide, setExpandedSlide] = useState<number | null>(0);

    const handleUpdateSlide = (index: number, field: keyof Slide, value: string) => {
        const newSlides = [...slides];
        newSlides[index] = { ...newSlides[index], [field]: value };
        setSlides(newSlides);
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-semibold text-gray-800">Review & Edit Slides</h2>
                <button
                    onClick={() => setCurrentStep(4)}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
                >
                    Proceed to Generate <ArrowRight size={18} />
                </button>
            </div>

            <div className="space-y-4">
                {slides.map((slide, index) => (
                    <div key={index} className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                        <button
                            onClick={() => setExpandedSlide(expandedSlide === index ? null : index)}
                            className="w-full flex justify-between items-center p-4 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
                        >
                            <span className="font-medium text-gray-700">Slide {slide.id}: {slide.title}</span>
                            {expandedSlide === index ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                        </button>

                        <AnimatePresence>
                            {expandedSlide === index && (
                                <motion.div
                                    initial={{ height: 0 }}
                                    animate={{ height: 'auto' }}
                                    exit={{ height: 0 }}
                                    className="overflow-hidden"
                                >
                                    <div className="p-6 space-y-4 border-t border-gray-200">
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                            <div className="md:col-span-2 space-y-4">
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                                                    <input
                                                        type="text"
                                                        value={slide.title}
                                                        onChange={(e) => handleUpdateSlide(index, 'title', e.target.value)}
                                                        className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                                                    <textarea
                                                        value={slide.content}
                                                        onChange={(e) => handleUpdateSlide(index, 'content', e.target.value)}
                                                        className="w-full p-2 border rounded-lg h-32 focus:ring-2 focus:ring-blue-500 outline-none"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">Image Prompt</label>
                                                    <textarea
                                                        value={slide.image_prompt}
                                                        onChange={(e) => handleUpdateSlide(index, 'image_prompt', e.target.value)}
                                                        className="w-full p-2 border rounded-lg h-20 focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                                                    />
                                                </div>
                                            </div>

                                            <div className="space-y-4">
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">Layout</label>
                                                    <select
                                                        value={slide.layout}
                                                        onChange={(e) => handleUpdateSlide(index, 'layout', e.target.value)}
                                                        className="w-full p-2 border rounded-lg outline-none"
                                                    >
                                                        <option value="Title_Image_Right">Image Right</option>
                                                        <option value="Title_Image_Left">Image Left</option>
                                                        <option value="Title_Only">Title Only</option>
                                                        <option value="Two_Column">Two Columns</option>
                                                    </select>
                                                </div>
                                                <div className="bg-gray-50 p-4 rounded-lg text-xs text-gray-500">
                                                    <p>Layout Preview:</p>
                                                    <div className="mt-2 aspect-video bg-white border border-gray-300 rounded flex items-center justify-center">
                                                        {slide.layout}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                ))}
            </div>
        </div>
    );
}
