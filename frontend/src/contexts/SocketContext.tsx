import type React from "react";
import { useCallback } from "react";
import {
  createContext,
  type ReactNode,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { io, type Socket } from "socket.io-client";
import type { Suggestion } from "./BpmnContext.tsx";

// URL API сервера
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface User {
  status: string;
  oid: string;
  rooms: string[];
}

interface EventsData {
  xml?: string;
  suggestions?: Suggestion[];
}

interface Events {
  pipeline_id: string;
  data: EventsData | Map<string, string | string[] | Map<string, string>>;
  step: string;
  status?: string;
}

interface SocketContextType {
  user: User | null;
  socket: Socket | null;
  connected: boolean;
  events: Events[];
  clearEvents: () => void;
}

const SocketContext = createContext<SocketContextType>({
  user: null,
  socket: null,
  connected: false,
  events: [],
  clearEvents: () => {},
});

export const useSocket = () => useContext(SocketContext);

interface SocketProviderProps {
  children: ReactNode;
}

export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState<Events[]>([]);

  useEffect(() => {
    const socketInstance = io(API_URL, {
      transports: ["websocket"],
      reconnectionAttempts: 100,
      reconnectionDelay: 1000,
      withCredentials: true,
    });

    socketInstance.on("connect", () => {
      setConnected(true);
    });

    socketInstance.on("disconnect", () => {
      setConnected(false);
    });

    socketInstance.on("pipeline", (event: Events) => {
      setEvents((prev) => [...prev, event]);
    });

    socketInstance.emit(
      "sub_to_notifications",
      (status: string, oid: string, rooms: string[]) =>
        setUser({
          status,
          oid,
          rooms,
        }),
    );

    setSocket(socketInstance);
    return () => {
      socketInstance.disconnect();
    };
  }, []);

  const clearEvents = useCallback(() => setEvents([]), []);

  const obj = useMemo(
    () => ({
      user,
      socket,
      connected,
      events,
      clearEvents,
    }),
    [user, socket, connected, events, clearEvents],
  );
  return (
    <SocketContext.Provider value={obj}>{children}</SocketContext.Provider>
  );
};
