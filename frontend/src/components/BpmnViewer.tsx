import type React from "react";
import { useEffect, useRef, useState } from "react";
import BpmnJS from "bpmn-js/dist/bpmn-navigated-viewer.production.min.js";
import "bpmn-js/dist/assets/diagram-js.css";
import "bpmn-js/dist/assets/bpmn-font/css/bpmn.css";
import { toast } from "react-toastify";
import type { BpmnError } from "../types";

interface BpmnViewerProps {
  xml: string | null;
  errors?: BpmnError[] | null;
  awaitingSuggestions?: boolean; // Новый проп для отображения ожидания
}

const PlaceholderIcon = () => (
  <svg
    width="44"
    height="44"
    fill="none"
    viewBox="0 0 44 44"
    className="mb-4 text-gray-400 mx-auto"
  >
    <rect
      x="8"
      y="8"
      width="28"
      height="28"
      rx="6"
      stroke="currentColor"
      strokeWidth="2"
      fill="#f3f4f6"
    />
    <rect
      x="16"
      y="16"
      width="12"
      height="12"
      rx="2"
      stroke="#cbd5e1"
      strokeWidth="2"
      fill="#e5e7eb"
    />
    <circle cx="22" cy="22" r="2.5" fill="#cbd5e1" />
  </svg>
);

const BpmnViewer: React.FC<BpmnViewerProps> = ({ xml, errors, awaitingSuggestions }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const outerRef = useRef<HTMLDivElement>(null);
  const bpmnViewerRef = useRef<BpmnJS | null>(null);
  const [isFullScreen, setIsFullScreen] = useState(false);

  // Инициализация просмотрщика BPMN
  useEffect(() => {
    if (!containerRef.current) return;
    bpmnViewerRef.current = new BpmnJS({
      container: containerRef.current,
    });

    const canvas = bpmnViewerRef.current.get("canvas");
    const resizeObserver = new ResizeObserver(() => {
      canvas.zoom("fit-viewport", "auto");
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      if (bpmnViewerRef.current) {
        bpmnViewerRef.current.destroy();
      }
      resizeObserver.disconnect();
    };
  }, []);

  // Импорт XML
  useEffect(() => {
    if (!bpmnViewerRef.current || !xml) return;
    bpmnViewerRef.current
      .importXML(xml)
      .then(({ warnings }: { warnings: any[] }) => {
        if (warnings.length) {
          console.warn("BPMN import warnings:", warnings);
        }
        const canvas = bpmnViewerRef.current?.get("canvas");
        canvas?.zoom("fit-viewport", "auto");
        toast.success("BPMN-диаграмма успешно отображена");
      })
      .catch((err: Error) => {
        console.error("BPMN import error:", err);
        toast.error("Ошибка при отображении BPMN-диаграммы");
      });
  }, [xml]);

  // Подсветка ошибок
  useEffect(() => {
    if (!bpmnViewerRef.current || !errors || errors.length === 0) return;
    try {
      const canvas = bpmnViewerRef.current.get("canvas");
      const elementRegistry = bpmnViewerRef.current.get("elementRegistry");
      const elements = elementRegistry.getAll();
      for (const element of elements) {
        if (element.id) {
          canvas.removeMarker(element.id, "error");
        }
      }
      for (const error of errors) {
        if (error.elementId) {
          canvas.addMarker(error.elementId, "error");
        }
      }
    } catch (error) {
      console.error("Error highlighting error elements:", error);
    }
  }, [errors]);

  // Полноэкранный режим
  useEffect(() => {
    const onFullScreenChange = () => {
      setIsFullScreen(document.fullscreenElement === outerRef.current);
    };
    document.addEventListener("fullscreenchange", onFullScreenChange);
    return () => {
      document.removeEventListener("fullscreenchange", onFullScreenChange);
    };
  }, []);

  const toggleFullScreen = () => {
    if (!outerRef.current) return;
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      outerRef.current.requestFullscreen();
    }
  };

  const downloadDiagram = async () => {
    if (!bpmnViewerRef.current) return;
    try {
      const { svg } = await bpmnViewerRef.current.saveSVG();
      const blob = new Blob([svg], { type: "image/svg+xml" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "diagram.svg";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Error saving SVG:", err);
      toast.error("Ошибка при сохранении диаграммы");
    }
  };

  return (
    <div
      ref={outerRef}
      className={`bpmn-viewer w-full h-full relative min-h-[350px] ${
        isFullScreen ? "bg-gray-50" : ""
      }`}
    >
      {!xml ? (
        <div className="flex flex-col justify-center items-center w-full h-full p-8 select-none">
          <PlaceholderIcon />
          <p className="text-lg font-medium text-gray-400 mb-2 text-center max-w-xs">
            Создайте описание процесса с помощью текста или голоса для
            визуализации BPMN-диаграммы
          </p>
        </div>
      ) : (
        <>
          <div
            ref={containerRef}
            className="w-full h-full"
            style={{ minHeight: "350px" }}
          />
          {awaitingSuggestions && (
            <div className="absolute bottom-2 left-0 right-0 text-center text-gray-500">
              Ожидание анализа диаграммы...
            </div>
          )}
          <div className="absolute top-2 right-2 flex space-x-2">
            <button
              onClick={downloadDiagram}
              className="bg-white p-2 rounded shadow"
              aria-label="Скачать диаграмму"
              title="Скачать диаграмму"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="black"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
            </button>
            <button
              onClick={toggleFullScreen}
              className="bg-white p-2 rounded shadow"
              aria-label={
                isFullScreen ? "Выйти из полноэкранного режима" : "На весь экран"
              }
              title={
                isFullScreen ? "Выйти из полноэкранного режима" : "На весь экран"
              }
            >
              {isFullScreen ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="black"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M8 3v3a2 2 0 0 1-2 2H3" />
                  <path d="M21 8h-3a2 2 0 0 1-2-2V3" />
                  <path d="M3 16h3a2 2 0 0 1 2 2v3" />
                  <path d="M16 21v-3a2 2 0 0 1 2-2h3" />
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="black"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M8 3H5a2 2 0 0 0-2 2v3" />
                  <path d="M21 8V5a2 2 0 0 0-2-2h-3" />
                  <path d="M3 16v3a2 2 0 0 0 2 2h3" />
                  <path d="M16 21h3a2 2 0 0 0 2-2v-3" />
                </svg>
              )}
            </button>
          </div>
        </>
      )}
      <style>
        {`
        .error {
          stroke: #E13C3C !important;
          stroke-width: 2px !important;
        }
        .djs-overlay-error {
          background-color: #E13C3C;
          color: white;
          border-radius: 2px;
          padding: 2px 5px;
          font-size: 12px;
        }
        `}
      </style>
    </div>
  );
};

export default BpmnViewer;