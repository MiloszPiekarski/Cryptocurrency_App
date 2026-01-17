'use client';

import { useState } from 'react';
import { X, HelpCircle } from 'lucide-react';

export function PageHelper({ title, description }: { title: string; description: string }) {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
            {/* Help Button */}
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-gradient-to-br from-purple-600 to-cyan-600 rounded-full flex items-center justify-center shadow-2xl hover:scale-110 transition-transform group"
            >
                <HelpCircle className="w-6 h-6 text-white group-hover:animate-bounce" />
            </button>

            {/* Modal */}
            {isOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" onClick={() => setIsOpen(false)}>
                    <div className="bg-gradient-to-br from-gray-900 to-black border-2 border-cyan-500/30 rounded-2xl p-8 max-w-md w-full relative" onClick={(e) => e.stopPropagation()}>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="absolute top-4 right-4 text-gray-500 hover:text-white"
                        >
                            <X className="w-5 h-5" />
                        </button>

                        <div className="text-4xl mb-4">🧠</div>
                        <h3 className="text-2xl font-bold text-white mb-3">{title}</h3>
                        <p className="text-gray-300 leading-relaxed">{description}</p>

                        <button
                            onClick={() => setIsOpen(false)}
                            className="mt-6 w-full bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-bold py-3 rounded-lg hover:scale-105 transition-transform"
                        >
                            Got it! 🚀
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}
