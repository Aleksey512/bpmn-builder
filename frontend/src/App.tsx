import { useEffect } from "react";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { SocketProvider, useSocket } from "./contexts/SocketContext";
import { BpmnProvider, useBpmn } from "./contexts/BpmnContext";
import BpmnViewer from "./components/BpmnViewer";
import ProcessInputForm from "./components/ProcessInputForm";
import ErrorsAndSuggestions from "./components/ErrorsAndSuggestions";
import { FaCircleNotch } from "react-icons/fa";

function AppContent() {
  const { events, connected, clearEvents } = useSocket();
  const {
    currentXml,
    errors,
    suggestions,
    processMode,
    loading,
    audioLoading,
    bpmnLoading,
    awaitingSuggestions,
    sendTextToPipeline,
    sendAudioToPipeline,
    applyCorrections,
    resetBpmnData,
  } = useBpmn();

  useEffect(() => {
    if (events.length === 0) return;
    clearEvents();
  }, [events, clearEvents]);

  const handleTextSubmit = async (text: string) => {
    await sendTextToPipeline(text);
  };

  const handleAudioSubmit = async (
    audioBlob: Blob,
  ): Promise<string | undefined> => {
    return await sendAudioToPipeline(audioBlob);
  };

  const handleNewProject = () => {
    resetBpmnData();
  };

  if (!connected) {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <FaCircleNotch className="animate-spin text-4xl text-primary-500 mb-4" />
        <p className="text-xl">Подключение к серверу...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <header className="pt-12 pb-6 px-6 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold mb-2 text-gray-900">
              Система визуализации BPMN-диаграмм
            </h1>
            <p className="mb-3 text-gray-700 text-base max-w-2xl">
              Сервис, который поможет аналитикам формировать диаграммы
              процессов:
            </p>
            <ul className="list-disc ml-8 text-gray-700 mb-0">
              <li>Аналитик описывает процесс голосом;</li>
              <li>Система генерирует диаграмму и отображает ее аналитику;</li>
              <li>
                Система в режиме чата с аналитиком вносит правки в диаграмму.
              </li>
            </ul>
          </div>
          <div className="flex gap-4 mt-2 md:mt-0">
            <button
              className="px-5 py-2.5 bg-white border border-gray-300 rounded-lg shadow-sm text-gray-800 font-medium hover:bg-gray-100 transition"
              onClick={handleNewProject}
            >
              <span className="inline-flex items-center gap-2">
                <svg
                  width="18"
                  height="18"
                  fill="none"
                  className="inline-block"
                >
                  <path
                    d="M9 2v14M2 9h14"
                    stroke="#222"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
                Новый проект
              </span>
            </button>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-6 items-start mb-16">
        <section>
          <div className="flex items-center justify-between mb-2 mt-2">
            <h2 className="font-semibold text-xl text-gray-900">
              {processMode === "create"
                ? "Создание диаграммы"
                : "Редактирование диаграммы"}
            </h2>
            <span className="ml-2 flex items-center text-xs font-medium text-gray-500">
              <span
                className={`w-2 h-2 rounded-full mr-2 ${processMode === "create" ? "bg-green-500" : "bg-blue-500"}`}
              />
              {processMode === "create" ? "Режим создания" : "Режим правки"}
            </span>
          </div>
          <ProcessInputForm
            onTextSubmit={handleTextSubmit}
            onAudioSubmit={handleAudioSubmit}
            loading={loading}
            audioLoading={audioLoading}
            bpmnLoading={bpmnLoading}
            awaitingSuggestions={awaitingSuggestions}
            processMode={processMode}
          />
          {(errors || suggestions) && (
            <ErrorsAndSuggestions
              errors={errors}
              suggestions={suggestions}
              onApplyCorrections={applyCorrections}
            />
          )}
        </section>
        <section>
          <div className="flex items-center justify-between mb-2 mt-2">
            <h2 className="font-semibold text-xl text-gray-900">
              BPMN-диаграмма
            </h2>
          </div>
          <div className="bg-gray-50 rounded-xl border border-gray-200 h-[415px] flex items-center justify-center min-h-[340px] overflow-hidden">
            <BpmnViewer xml={currentXml} errors={errors} awaitingSuggestions={awaitingSuggestions} />
          </div>
        </section>
      </main>
      <ToastContainer position="bottom-right" theme="colored" />
    </div>
  );
}

export default function App() {
  return (
    <SocketProvider>
      <BpmnProvider>
        <AppContent />
      </BpmnProvider>
    </SocketProvider>
  );
}