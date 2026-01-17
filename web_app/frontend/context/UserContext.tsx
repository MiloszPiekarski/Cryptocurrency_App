'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { getAuth, onAuthStateChanged, User } from 'firebase/auth';
import { initializeApp, getApps, getApp } from "firebase/app";

// Re-use simple firebase config or import from lib
// Assuming lib/firebase.ts exists and initializes app
import { app } from '../lib/firebase'; // Adjust path if needed

const auth = getAuth(app);
const BACKEND_URL = "http://localhost:8000/api"; // Adjust if needed

interface UserContextType {
    user: User | null;
    plan: 'FREE' | 'PRO' | null;
    loading: boolean;
    refreshPlan: () => Promise<void>;
    upgradeToPro: () => Promise<void>;
}

const UserContext = createContext<UserContextType>({
    user: null,
    plan: null,
    loading: true,
    refreshPlan: async () => { },
    upgradeToPro: async () => { },
});

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [plan, setPlan] = useState<'FREE' | 'PRO' | null>(null);
    const [loading, setLoading] = useState(true);

    const syncUser = async (currentUser: User) => {
        try {
            const res = await fetch(`${BACKEND_URL}/auth/sync`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    firebase_uid: currentUser.uid,
                    email: currentUser.email
                })
            });
            const data = await res.json();
            setPlan(data.plan || 'FREE');
        } catch (e) {
            console.error("Sync failed", e);
            setPlan('FREE');
        }
    };

    const upgradeToPro = async () => {
        if (!user) return;
        try {
            await fetch(`${BACKEND_URL}/payment/simulate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ firebase_uid: user.uid })
            });
            setPlan('PRO');
        } catch (e) {
            console.error("Upgrade failed", e);
        }
    };

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, async (u) => {
            setUser(u);
            if (u) {
                await syncUser(u);
            } else {
                setPlan(null);
            }
            setLoading(false);
        });
        return () => unsubscribe();
    }, []);

    return (
        <UserContext.Provider value={{
            user,
            plan,
            loading,
            refreshPlan: async () => { if (user) await syncUser(user); },
            upgradeToPro
        }}>
            {children}
        </UserContext.Provider>
    );
};

export const useUser = () => useContext(UserContext);
