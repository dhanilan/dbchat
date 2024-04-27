

import { create } from "zustand";
import { BaseApi } from "../api/baseApi";

export interface AppSetting {
    oai_api_key: string;
    analytics_db_url: string;
    customer_id?: string;

}


export type AppSettingStoreType = {
    appSetting: AppSetting;
    loading: boolean;
    getAppSetting: () => Promise<void>;
    updateAppSetting: (appSetting: AppSetting) => Promise<void>;
}
export const appSettingStore = create<AppSettingStoreType>((set, get, _) => ({
    appSetting: {
        oai_api_key: '',
        analytics_db_url: '',
        customer_id: '',
    },
    loading: false,
    getAppSetting: async () => {
        set({ loading: true });
        const api = new BaseApi();
        const appSetting = await api.GetOne<AppSetting>('settings');
        if (appSetting) {
            set({ appSetting, loading: false });
        }
        else {
            set({ loading: false });
        }
    },
    updateAppSetting: async (appSetting: AppSetting) => {
        set({ loading: true });
        const api = new BaseApi();
        const updatedAppSetting = await api.create<AppSetting>('settings', appSetting);
        set({ appSetting: updatedAppSetting, loading: false });
    }
}));