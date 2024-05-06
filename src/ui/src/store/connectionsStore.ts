
import { create } from "zustand";
import { BaseApi } from "../api/baseApi";

export interface Connection {
    id?: string;
    name?: string;
    customer_id?: string;
    validated?: boolean;
    connection_string?: string;
    connection_schema?: any;
}

export type ConnectionsStoreType = {
    connections: Connection[];
    connection: Connection;
    loading: boolean;
    getConnections: (setCurrent: boolean) => Promise<void>;
    initialize: () => void;
    setCurrentConnection: (connection: Connection) => void;
    createConnection: (connection: Connection) => Promise<void>;
    updateConnection: (connection: Connection) => Promise<void>;
    deleteConnection: (id: string) => Promise<void>;
    createSchema: (connection: Connection) => Promise<void>;
}
export const connectionsStore = create<ConnectionsStoreType>((set, get, _) => ({
    connections: [],

    connection: {
        name: '',
        connection_string: '',
        connection_schema: {},
        customer_id: 'default'
    },
    loading: false,
    initialize: async () => {

        // get all connections
        try {
            await get().getConnections(true);
            // set the first connection as the current connection

        }
        catch (e) {
            console.log(e);
        }

    },
    setCurrentConnection: (connection: Connection) => {
        set({ connection });
    },
    getConnections: async (setCurrent: boolean = false) => {
        set({ loading: true });
        const api = new BaseApi();
        const connections = await api.Get<Connection>('connections');
        if (connections) {
            set({ connections, loading: false });
        }
        else {
            set({ loading: false });
        }
        if (setCurrent && connections.length > 0) {
            set({ connection: connections[0] });
        }
    },
    createConnection: async (connection: Connection) => {
        set({ loading: true });

        const api = new BaseApi();
        connection.customer_id = 'default';
        const createdConnection = await api.create<Connection>('connections', connection);
        set({ connections: [...get().connections, createdConnection], loading: false });
        set({ connection: createdConnection })
    },
    updateConnection: async (connection: Connection) => {
        set({ loading: true });
        const api = new BaseApi();
        const updatedConnection = await api.update<Connection>('connections', connection);
        const connections = get().connections.map((c) => {
            if (c.customer_id === updatedConnection.customer_id) {
                return updatedConnection;
            }
            return c;
        });
        set({ connections, loading: false });
    },
    deleteConnection: async (id: string) => {
        set({ loading: true });
        const api = new BaseApi();
        await api.delete<Connection>('connections', id);
        const connections = get().connections.filter((c) => c.customer_id !== id);
        set({ connections, loading: false });
    },
    createSchema: async () => {
        set({ loading: true });
        const api = new BaseApi();
        const currentConnection = get().connection;

        const schema = await api.create<Connection>(`connections/${currentConnection.id || 'new'}/schema`, currentConnection);
        set({ connection: { ...currentConnection, connection_schema: schema }, loading: false });
    }
}));