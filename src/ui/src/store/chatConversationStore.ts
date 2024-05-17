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
    connection_id: string;
    messages: ConversationMessage[];
};
type ChatConversationStore = {
    allConversations: any[];
    wait_for_server: boolean;
    title: string;
    messages: ConversationMessage[];
    currentConverstationId: string;
    initialize: (conversationId?: string) => Promise<void>;
    addMessage: (message: ConversationMessage, currentConnectionId: string) => Promise<void>;
    fetchAllConversations: () => Promise<void>;
    createConversation: (connectionId: string, title?: string) => Promise<void>;
    deleteConversation: (conversationId: string) => Promise<void>;

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

                set({ messages: messages, wait_for_server: false });


            } catch (error) {
                console.log('Failed to fetch messages');
                set({ wait_for_server: false });
            }

            set({ wait_for_server: false });
        }
    },
    fetchAllConversations: async () => {
        const api = new BaseApi();
        try {
            const conversations = await api.Get<Conversation>('conversation');
            set({ allConversations: conversations as any[] });
            if (conversations.length > 0 && !get().currentConverstationId) {
                set({ currentConverstationId: conversations[0].id, title: conversations[0].title });
                get().initialize(conversations[0].id);
            }
            else {

                // // create a new conversation
                // set({ currentConverstationId: '', title: 'New Conversation' });
                // set({ wait_for_server: true });

                // const api = new BaseApi();
                // try {
                //     const created_id: string = await api.create('conversation', { title: 'New Conversation' });

                //     set({ wait_for_server: false, currentConverstationId: created_id });
                //     get().initialize(created_id);
                // } catch (error) {
                //     set({ wait_for_server: false });
                //     console.log('Failed to create conversation');

                // }

            }
            console.log(conversations);
        } catch (error) {
            console.log('Failed to fetch conversations');
        }
    },

    addMessage: async (message: ConversationMessage, currentConnectionId: string) => {
        // Add the message to the conversation
        set((state) => ({ messages: [...state.messages, message], wait_for_server: true }));
        // Send the message to the server

        const api = new BaseApi();
        let conversation_id = get().currentConverstationId;
        let newConversation = false;

        try {

            if (!conversation_id) {
                newConversation = true;
                // create a new conversation
                // get().createConversation(currentConnectionId, 'New Conversation');
                conversation_id = await api.create('conversation', {
                    connection_id: currentConnectionId,
                    title: 'New Conversation' + new Date().toLocaleString()
                });

            }

            const response_message: ConversationMessage = await api.create(`conversation/${conversation_id}/messages`, message);

            set((state) => ({ messages: [...state.messages, response_message], currentConverstationId: conversation_id, wait_for_server: false }));
            if (newConversation) {
                get().fetchAllConversations();
            }
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
    createConversation: async (connectionId: string, title: string = 'New Conversation') => {
        // Create a new conversation
        set({ wait_for_server: true });
        const api = new BaseApi();
        try {
            const created_id: string = await api.create('conversation', { connection_id: connectionId, title: title });
            set({ wait_for_server: false, currentConverstationId: created_id });
            get().initialize(created_id);
        } catch (error) {
            console.log('Failed to create conversation');
            set({ wait_for_server: false });
        }
    },
    deleteConversation: async (conversationId: string) => {
        // Delete the conversation from the server
        set({ wait_for_server: true });
        const api = new BaseApi();
        try {
            await api.delete(`conversation`, conversationId);
            set({ wait_for_server: false });
            get().fetchAllConversations();
        } catch (error) {
            console.log('Failed to delete conversation');
            set({ wait_for_server: false });
        }
    }

}));