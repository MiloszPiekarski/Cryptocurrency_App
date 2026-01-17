"use client";

import { useAlertStore } from '@/lib/alertStore';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertTriangle, XCircle, Info, X } from 'lucide-react';

export function AlertsContainer() {
    const { alerts, removeAlert } = useAlertStore();

    return (
        <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
            <AnimatePresence>
                {alerts.map((alert) => (
                    <motion.div
                        key={alert.id}
                        initial={{ opacity: 0, x: 50, scale: 0.9 }}
                        animate={{ opacity: 1, x: 0, scale: 1 }}
                        exit={{ opacity: 0, x: 20 }}
                        className="pointer-events-auto w-80 bg-[#0f1729] border border-gray-800 rounded-lg shadow-2xl overflow-hidden flex"
                    >
                        <div className={`w-1 ${alert.type === 'success' ? 'bg-green-500' :
                                alert.type === 'error' ? 'bg-red-500' :
                                    alert.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                            }`} />

                        <div className="flex-1 p-3 flex items-start gap-3">
                            <div className="mt-0.5">
                                {alert.type === 'success' && <CheckCircle className="w-5 h-5 text-green-400" />}
                                {alert.type === 'error' && <XCircle className="w-5 h-5 text-red-400" />}
                                {alert.type === 'warning' && <AlertTriangle className="w-5 h-5 text-yellow-400" />}
                                {alert.type === 'info' && <Info className="w-5 h-5 text-blue-400" />}
                            </div>
                            <div className="flex-1">
                                <h4 className="text-sm font-semibold text-white">{alert.title}</h4>
                                <p className="text-xs text-gray-400 mt-1">{alert.message}</p>
                            </div>
                            <button
                                onClick={() => removeAlert(alert.id)}
                                className="text-gray-500 hover:text-white transition-colors"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    </motion.div>
                ))}
            </AnimatePresence>
        </div>
    );
}
