import { create } from 'zustand';

export interface Slide {
    id: number;
    title: string;
    content: string;
    image_prompt: string;
    layout: string;
    image_base64?: string;
}

interface PresentationState {
    apiKey: string;
    setApiKey: (key: string) => void;
    topic: string;
    setTopic: (topic: string) => void;
    language: string;
    setLanguage: (lang: string) => void;
    slideCount: number;
    setSlideCount: (count: number) => void;
    slides: Slide[];
    setSlides: (slides: Slide[]) => void;
    currentStep: number;
    setCurrentStep: (step: number) => void;
    isLoading: boolean;
    setIsLoading: (loading: boolean) => void;
    fileName: string;
    setFileName: (name: string) => void;
    materials: string;
    setMaterials: (materials: string) => void;
}

export const usePresentationStore = create<PresentationState>((set) => ({
    apiKey: '',
    setApiKey: (key) => set({ apiKey: key }),
    topic: '',
    setTopic: (topic) => set({ topic }),
    language: 'Korean',
    setLanguage: (language) => set({ language }),
    slideCount: 10,
    setSlideCount: (slideCount) => set({ slideCount }),
    slides: [],
    setSlides: (slides) => set({ slides }),
    currentStep: 1,
    setCurrentStep: (currentStep) => set({ currentStep }),
    isLoading: false,
    setIsLoading: (isLoading) => set({ isLoading }),
    fileName: 'presentation',
    setFileName: (fileName) => set({ fileName }),
    materials: '',
    setMaterials: (materials) => set({ materials }),
}));
