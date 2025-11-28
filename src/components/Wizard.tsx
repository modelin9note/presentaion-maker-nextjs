'use client';

import { usePresentationStore } from '@/store/usePresentationStore';
import SetupStep from './steps/SetupStep';
import DraftStep from './steps/DraftStep';
import EditStep from './steps/EditStep';
import GenerateStep from './steps/GenerateStep';
import { motion, AnimatePresence } from 'framer-motion';

export default function Wizard() {
    const { currentStep } = usePresentationStore();

    return (
        <div className="max-w-4xl mx-auto p-6">
            <div className="mb-8">
                <div className="flex justify-between items-center mb-4">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Advanced Academic PPT Generator
                    </h1>
                    <span className="text-sm text-gray-500">Step {currentStep} of 4</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full">
                    <div
                        className="h-full bg-blue-600 rounded-full transition-all duration-500"
                        style={{ width: `${(currentStep / 4) * 100}%` }}
                    />
                </div>
            </div>

            <AnimatePresence mode="wait">
                <motion.div
                    key={currentStep}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                >
                    {currentStep === 1 && <SetupStep />}
                    {currentStep === 2 && <DraftStep />}
                    {currentStep === 3 && <EditStep />}
                    {currentStep === 4 && <GenerateStep />}
                </motion.div>
            </AnimatePresence>
        </div>
    );
}
