import { create } from 'zustand';
import { BaseApi } from '../api/baseApi';


export type ConversationMessage = {
    id?: string;
    conversationId: string;
    text: string;
    sender: string;
    isUser: boolean;
    timestamp: Date;
};
type ChatConversationStore = {
    wait_for_server: boolean;
    messages: ConversationMessage[];
    currentConverstationId: string;
    initialize: (conversationId?: string) => Promise<void>;
    addMessage: (message: ConversationMessage) => Promise<void>;

};

export const conversationStore = create<ChatConversationStore>((set, get) => ({
    wait_for_server: false,
    messages: [],
    currentConverstationId: '',
    initialize: async (conversationId?: string) => {
        // Fetch messages from the server
        if (conversationId) {
            // Fetch messages for the conversation id
            set({ currentConverstationId: conversationId });
            set({ wait_for_server: true });
            // Fetch messages from the server

            set({ wait_for_server: false });
        } else {
            // create a new conversation
            set({ currentConverstationId: 'default' });
            set({ wait_for_server: true });

            const api = new BaseApi();
            try {
                const created_id: string = await api.create('conversations', { name: '' });

                set({ wait_for_server: false, currentConverstationId: created_id });
            } catch (error) {
                set({ wait_for_server: false });
            }


        }
    },

    addMessage: async (message: ConversationMessage) => {
        // Add the message to the conversation
        set((state) => ({ messages: [...state.messages, message], wait_for_server: true }));
        // Send the message to the server

        const api = new BaseApi();

        try {
            const response_message: ConversationMessage = await api.create('conversations/message', message);
            set((state) => ({ messages: [...state.messages, response_message] }));

        }
        catch (error) {
            console.log('Failed to send message');
            const failed_message = <ConversationMessage>{
                id: 'failed',
                conversationId: message.conversationId,
                text: 'Failed to send message',
                sender: 'System',
                isUser: false,
                timestamp: new Date(),
            };

            set({ wait_for_server: false, messages: [...get().messages, failed_message] });
        }


    },

}));