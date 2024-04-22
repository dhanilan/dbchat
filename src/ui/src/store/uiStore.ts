import { create } from 'zustand';
import { MenuItem } from '../types';
type UIStore = {
    menuItems: MenuItem[];
    isLoading: boolean;
    setMenuItems: (items: MenuItem[]) => void;
    setLoading: (loading: boolean) => void;
};

const defaultMenuItems = [
    { label: 'Home', url: '/', icon: 'bx bx-home' },
    { label: 'Settings', url: '/settings', icon: 'bx bx-cog' },
];

export const uiStore = create<UIStore>((set) => ({
    menuItems: defaultMenuItems,
    isLoading: false,
    setMenuItems: (items) => set({ menuItems: items }),
    setLoading: (loading) => set({ isLoading: loading }),
}));