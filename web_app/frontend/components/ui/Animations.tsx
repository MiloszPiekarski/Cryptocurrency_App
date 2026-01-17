/**
 * Animation Wrappers - DRAMATIC VERSION
 * Highly visible animations that WOW users!
 */

'use client';

import { motion, HTMLMotionProps } from 'framer-motion';
import { ReactNode } from 'react';

// Slide in from LEFT (for left panel)
export function SlideInLeft({
    children,
    delay = 0,
    className = '',
}: {
    children: ReactNode;
    delay?: number;
    className?: string;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{
                duration: 0.8,
                delay,
                type: "spring",
                stiffness: 100,
                damping: 15
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

// Slide in from RIGHT (for right panel)
export function SlideInRight({
    children,
    delay = 0,
    className = '',
}: {
    children: ReactNode;
    delay?: number;
    className?: string;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{
                duration: 0.8,
                delay,
                type: "spring",
                stiffness: 100,
                damping: 15
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

// Pop in from bottom (for center panel)
export function PopIn({
    children,
    delay = 0,
    className = '',
}: {
    children: ReactNode;
    delay?: number;
    className?: string;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 30 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{
                duration: 0.7,
                delay,
                type: "spring",
                stiffness: 120,
                damping: 12
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

// Fade in from bottom
export function FadeInUp({
    children,
    delay = 0,
    className = '',
}: {
    children: ReactNode;
    delay?: number;
    className?: string;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay, ease: [0.25, 0.1, 0.25, 1] }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

// Fade in (simple)
export function FadeIn({
    children,
    delay = 0,
    className = '',
}: {
    children: ReactNode;
    delay?: number;
    className?: string;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay, ease: 'easeOut' }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

// Scale in (for cards/panels)
export function ScaleIn({
    children,
    delay = 0,
    className = '',
}: {
    children: ReactNode;
    delay?: number;
    className?: string;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay, ease: [0.25, 0.1, 0.25, 1] }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

// Stagger children
export function StaggerContainer({
    children,
    className = '',
}: {
    children: ReactNode;
    className?: string;
}) {
    return (
        <motion.div
            initial="hidden"
            animate="visible"
            variants={{
                hidden: { opacity: 0 },
                visible: {
                    opacity: 1,
                    transition: {
                        staggerChildren: 0.1,
                    },
                },
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

export function StaggerItem({
    children,
    className = '',
}: {
    children: ReactNode;
    className?: string;
}) {
    return (
        <motion.div
            variants={{
                hidden: { opacity: 0, y: 10 },
                visible: { opacity: 1, y: 0 },
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

// Hover scale (for interactive elements)
export function HoverScale({
    children,
    scale = 1.02,
    className = '',
}: {
    children: ReactNode;
    scale?: number;
    className?: string;
}) {
    return (
        <motion.div
            whileHover={{ scale }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className={className}
        >
            {children}
        </motion.div>
    );
}
