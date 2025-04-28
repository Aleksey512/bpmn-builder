import type React from "react";
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { useSocket } from "./SocketContext";
import type { BpmnRequest } from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface BpmnError {
  id: string;
  type: "topological" | "logical";
  message: string;
  elementId?: string;
}

export interface Suggestion {
  error: string;
  correction: string;
}

export type ProcessMode = "create" | "edit";

interface BpmnContextType {
  currentXml: string | null;
  errors: BpmnError[];
  suggestions: Suggestion[];
  processMode: ProcessMode;
  loading: boolean;
  audioLoading: boolean;
  bpmnLoading: boolean;
  awaitingSuggestions: boolean;
  currentPipelineId: string | null;
  setBpmnData: (xml: string) => void;
  resetBpmnData: () => void;
  sendTextToPipeline: (text: string) => Promise<void>;
  sendAudioToPipeline: (audioBlob: Blob) => Promise<string | undefined>;
  applyCorrections: (corrections: string[]) => Promise<void>;
}

const defaultBpmnContext: BpmnContextType = {
  currentXml: null,
  errors: [],
  suggestions: [],
  processMode: "create",
  loading: false,
  audioLoading: false,
  bpmnLoading: false,
  awaitingSuggestions: false,
  currentPipelineId: null,
  setBpmnData: () => {},
  resetBpmnData: () => {},
  sendTextToPipeline: async () => {},
  sendAudioToPipeline: async () => undefined,
  applyCorrections: async () => {},
};

const BpmnContext = createContext<BpmnContextType>(defaultBpmnContext);

export const useBpmn = () => useContext(BpmnContext);

const DEFAULT_XML = `<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
    xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
    xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
    xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
    id="definitions_1">
  <process id="Process_1">
    <startEvent id="StartEvent_1" />
    <endEvent id="EndEvent_1" />
    <sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="EndEvent_1" />
  </process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="StartEvent_1_di" bpmnElement="StartEvent_1">
        <dc:Bounds x="150" y="100" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndEvent_1_di" bpmnElement="EndEvent_1">
        <dc:Bounds x="250" y="100" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <di:waypoint x="186" y="118" />
        <di:waypoint x="250" y="118" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</definitions>`

export const BpmnProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const { user, events, clearEvents } = useSocket();
  const [currentXml, setCurrentXml] = useState<string | null>(DEFAULT_XML);
  const [errors, setErrors] = useState<BpmnError[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [processMode, setProcessMode] = useState<ProcessMode>("create");
  const [loading, setLoading] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const [bpmnLoading, setBpmnLoading] = useState(false);
  const [awaitingSuggestions, setAwaitingSuggestions] = useState(false);
  const [currentPipelineId, setCurrentPipelineId] = useState<string | null>(null);

  useEffect(() => {
    if (!events.length) return;
    for (const event of events) {
      if (typeof event.data === "object" && !(event.data instanceof Map)) {
        if (event.step === "bpmn") {
          if (event.status !== "error" && event.data.xml) {
            setCurrentXml(event.data.xml);
            setProcessMode("edit");
            setErrors([]);
            setBpmnLoading(false);
            setAwaitingSuggestions(true);
          } else if (event.status === "error") {
            toast.error("Ошибка генерации BPMN-диаграммы");
            setBpmnLoading(false);
          }
        }
        if (event.step === "suggestions") {
          if (event.status !== "error" && event.data.suggestions) {
            setSuggestions(event.data.suggestions);
            setAwaitingSuggestions(false);
          } else if (event.status === "error") {
            toast.error("Ошибка получения предложений по исправлению");
            setAwaitingSuggestions(false);
          }
        }
      }
    }
    clearEvents();
  }, [events, clearEvents]);

  const handleDescription = useCallback(
    async (description: string, bpmnXml?: string | null) => {
      if (!user) return;
      try {
        setLoading(true);
        setBpmnLoading(true);
        const body: BpmnRequest = {
          user_id: user.oid,
          text: description,
        };
        if (bpmnXml) body.bpmn_xml = bpmnXml;
        await axios.post(`${API_URL}/pipeline/from_text`, body);
      } catch (e) {
        toast.error("Ошибка отправки описания.");
        setBpmnLoading(false);
      } finally {
        setLoading(false);
      }
    },
    [user],
  );

  const sendTextToPipeline = useCallback(
    async (text: string) => {
      setSuggestions([]);
      await handleDescription(text, currentXml);
    },
    [currentXml, handleDescription],
  );

  const sendAudioToPipeline = useCallback(async (audioBlob: Blob) => {
    setSuggestions([]);
    setAudioLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", audioBlob, "audio.webm");
      const response = await axios.post(
        `${API_URL}/stt/upload_audio`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } },
      );
      toast.info("Речь успешно распознана");
      return response.data.text;
    } catch {
      toast.error("Ошибка распознавания речи");
      return undefined;
    } finally {
      setAudioLoading(false);
    }
  }, []);

  const applyCorrections = useCallback(
    async (corrections: string[]) => {
      const text = corrections.join("\n");
      await handleDescription(text, currentXml);
      setSuggestions([]);
    },
    [currentXml, handleDescription],
  );

  const setBpmnData = useCallback((xml: string) => {
    setCurrentXml(xml);
    setProcessMode("edit");
  }, []);

  const resetBpmnData = useCallback(() => {
    setCurrentXml(DEFAULT_XML);
    setErrors([]);
    setSuggestions([]);
    setProcessMode("create");
    setCurrentPipelineId(null);
    setAwaitingSuggestions(false);
  }, []);

  const contextValue = useMemo(
    () => ({
      currentXml,
      errors,
      suggestions,
      processMode,
      loading,
      audioLoading,
      bpmnLoading,
      awaitingSuggestions,
      currentPipelineId,
      setBpmnData,
      resetBpmnData,
      sendTextToPipeline,
      sendAudioToPipeline,
      applyCorrections,
    }),
    [
      currentXml,
      errors,
      suggestions,
      processMode,
      loading,
      audioLoading,
      bpmnLoading,
      awaitingSuggestions,
      currentPipelineId,
      setBpmnData,
      resetBpmnData,
      sendTextToPipeline,
      sendAudioToPipeline,
      applyCorrections,
    ],
  );

  return (
    <BpmnContext.Provider value={contextValue}>
      {children}
    </BpmnContext.Provider>
  );
};