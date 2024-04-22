import { create } from 'zustand';
import { BaseApi } from '../api/baseApi';


export type ConversationMessage = {
    id?: string;
    conversation_id: string;
    text: string;
    sender: string;
    isUser: boolean;
    timestamp: Date;
};
export type Conversation = {
    id: string;
    title: string;
    messages: ConversationMessage[];
};
type ChatConversationStore = {
    allConversations: any[];
    wait_for_server: boolean;
    title: string;
    messages: ConversationMessage[];
    currentConverstationId: string;
    initialize: (conversationId?: string) => Promise<void>;
    addMessage: (message: ConversationMessage) => Promise<void>;
    fetchAllConversations: () => Promise<void>;

};

export const conversationStore = create<ChatConversationStore>((set, get) => ({
    wait_for_server: false,
    messages: [],
    allConversations: [],
    currentConverstationId: '',
    title: '',
    initialize: async (conversationId?: string) => {
        // Fetch messages from the server
        if (conversationId) {
            // Fetch messages for the conversation id
            set({ currentConverstationId: conversationId });
            set({ wait_for_server: true });
            // Fetch messages from the server
            const api = new BaseApi();
            try {
                const messages = await api.Get<ConversationMessage>(`conversation/${conversationId}/messages`);
                if (messages && messages.length > 0) {
                    set({ messages: messages, wait_for_server: false });
                }

            } catch (error) {
                console.log('Failed to fetch messages');
                set({ wait_for_server: false });
            }

            set({ wait_for_server: false });
        } else {
            // create a new conversation
            set({ currentConverstationId: '', title: 'New Conversation' });
            set({ wait_for_server: true });

            const api = new BaseApi();
            try {
                const created_id: string = await api.create('conversation', { title: '' });

                set({ wait_for_server: false, currentConverstationId: created_id });
            } catch (error) {
                set({ wait_for_server: false });
            }


        }
    },
    fetchAllConversations: async () => {
        const api = new BaseApi();
        try {
            const conversations = await api.Get<Conversation>('conversation');
            set({ allConversations: conversations as any[] });
            if (conversations.length > 0) {
                set({ currentConverstationId: conversations[0].id, title: conversations[0].title });
                get().initialize(conversations[0].id);
            }
            else {
                get().initialize();
            }
            console.log(conversations);
        } catch (error) {
            console.log('Failed to fetch conversations');
        }
    },

    addMessage: async (message: ConversationMessage) => {
        // Add the message to the conversation
        set((state) => ({ messages: [...state.messages, message], wait_for_server: true }));
        // Send the message to the server

        const api = new BaseApi();

        try {
            const response_message: ConversationMessage = await api.create(`conversation/${get().currentConverstationId}/messages`, message);
            set((state) => ({ messages: [...state.messages, response_message] }));

        }
        catch (error) {
            console.log('Failed to send message');
            const failed_message = <ConversationMessage>{
                id: 'failed',
                conversation_id: message.conversation_id,
                text: 'Failed to send message',
                sender: 'System',
                isUser: false,
                timestamp: new Date(),
            };

            set({ wait_for_server: false, messages: [...get().messages, failed_message] });
        }


    },

}));