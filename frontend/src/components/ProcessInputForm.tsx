import type React from "react";
import { useState } from "react";
import { FaMicrophone, FaPaperPlane, FaStop } from "react-icons/fa";
import type { ProcessMode } from "../types";

interface ProcessInputFormProps {
  onTextSubmit: (text: string) => Promise<void>;
  onAudioSubmit: (audioBlob: Blob) => Promise<string | undefined>;
  loading: boolean;
  audioLoading: boolean;
  bpmnLoading: boolean;
  awaitingSuggestions: boolean;
  processMode: ProcessMode;
}

const ProcessInputForm: React.FC<ProcessInputFormProps> = ({
  onTextSubmit,
  onAudioSubmit,
  loading,
  audioLoading,
  bpmnLoading,
  awaitingSuggestions,
  processMode,
}) => {
  const [processDescription, setProcessDescription] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [recorder, setRecorder] = useState<MediaRecorder | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);

  const addSecond = () => {
    setRecordingTime((t) => t + 1);
  };

  // --- Голосовая запись ---
  const handleStartRecording = async () => {
    setRecordingTime(0);
    setIsRecording(true);

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const rec = new MediaRecorder(stream);
    setRecorder(rec);

    const chunks: BlobPart[] = [];

    rec.ondataavailable = (e) => {
      chunks.push(e.data);
    };

    let timer: number;

    rec.onstart = () => {
      timer = setInterval(addSecond, 1000);
    };

    rec.onerror = () => {
      clearInterval(timer);
    };

    rec.onstop = () => {
      clearInterval(timer);
      const blob = new Blob(chunks, { type: "audio/webm" });
      onAudioSubmit(blob).then((text) => text && setProcessDescription(text));
      for (const t of stream.getTracks()) {
        t.stop();
      }
    };
    rec.start();
  };

  const handleStopRecording = () => {
    if (recorder && isRecording) {
      recorder.stop();
      setIsRecording(false);
    }
  };

  const formatTime = (s: number) =>
    `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

  // --- Отправка текста ---
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (processDescription.trim()) {
      await onTextSubmit(processDescription.trim());
      setProcessDescription("");
    }
  };

  // Определение, заблокирован ли ввод
  const isInputDisabled = loading || isRecording || audioLoading || bpmnLoading || awaitingSuggestions;

  return (
    <form onSubmit={handleSubmit} className="relative" autoComplete="off">
      <div className="bg-gray-50 border border-gray-200 rounded-xl px-4 pt-4 pb-6 relative transition group">
        <textarea
          disabled={isInputDisabled}
          className="w-full resize-none min-h-[88px] max-h-[140px] bg-transparent text-base rounded-xl text-gray-900 focus:outline-none placeholder-gray-400 block pr-[90px] overflow-hidden"
          placeholder={
            processMode === "create"
              ? "Опишите ваш бизнес-процесс."
              : "Редактируйте существующее описание..."
          }
          value={processDescription}
          onChange={(e) => setProcessDescription(e.target.value)}
        />
        <div className="absolute right-3 top-1/3 flex flex-col items-end">
          <button
            type="submit"
            className="w-12 h-12 flex items-center justify-center bg-green-50 border border-green-200 rounded-full text-green-600 hover:bg-green-100 shadow disabled:hover:bg-green-50 disabled:opacity-70"
            aria-label="Отправить"
            disabled={isInputDisabled || !processDescription.trim()}
          >
            <FaPaperPlane />
          </button>
        </div>
      </div>
      {/* Статус голосовой записи */}
      {isRecording && (
        <div className="relative mt-2 px-4 py-2 rounded border border-red-200 bg-red-50 text-red-700 text-sm flex items-center gap-2 animate-fade-in">
          <div className="absolute z-10 left-1/2 transform -translate-x-1/2 top-auto w-full flex justify-center pointer-events-none">
            <button
              type="button"
              className="pointer-events-auto w-12 h-12 flex items-center justify-center hover:bg-red-600 transition animate-in bg-white border-4 border-red-200 shadow-xl rounded-full text-red-500 animate-pulse"
              onClick={handleStopRecording}
              aria-label="Остановить запись"
            >
              <FaStop className="text-2xl" />
            </button>
          </div>
          <span className="inline-block w-3 h-3 rounded-full bg-red-400 mr-2" />{" "}
          Запись голоса...{" "}
          <span className="font-mono ml-2">{formatTime(recordingTime)}</span>
        </div>
      )}
      {/* Индикатор загрузки аудио */}
      {audioLoading && (
        <div className="relative mt-2 px-4 py-2 rounded border border-blue-200 bg-blue-50 text-blue-700 text-sm flex items-center gap-2 animate-fade-in">
          <span className="inline-block w-3 h-3 rounded-full bg-blue-400 mr-2" />{" "}
          Обработка аудио...
        </div>
      )}
      {/* Индикатор загрузки BPMN */}
      {bpmnLoading && (
        <div className="relative mt-2 px-4 py-2 rounded border border-blue-200 bg-blue-50 text-blue-700 text-sm flex items-center gap-2 animate-fade-in">
          <span className="inline-block w-3 h-3 rounded-full bg-blue-400 mr-2" />{" "}
          Генерация BPMN-диаграммы...
        </div>
      )}
      {/* Индикатор ожидания анализа */}
      {awaitingSuggestions && (
        <div className="relative mt-2 px-4 py-2 rounded border border-yellow-200 bg-yellow-50 text-yellow-700 text-sm flex items-center gap-2 animate-fade-in">
          <span className="inline-block w-3 h-3 rounded-full bg-yellow-400 mr-2" />{" "}
          Ожидание анализа диаграммы...
        </div>
      )}
      {/* Кнопка для голосового режима */}
      {!isRecording && (
        <div className="absolute z-10 left-1/2 transform -translate-x-1/2 top-auto bottom-[-54px] w-full flex justify-center pointer-events-none">
          <button
            type="button"
            className="pointer-events-auto w-12 h-12 bg-blue-500 shadow-xl text-white rounded-full flex items-center justify-center border-4 border-white hover:bg-blue-600 transition animate-in"
            onClick={handleStartRecording}
            disabled={isInputDisabled}
            aria-label="Начать запись голоса"
          >
            <FaMicrophone className="text-2xl" />
          </button>
        </div>
      )}
    </form>
  );
};

export default ProcessInputForm;