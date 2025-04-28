interface BpmnWarning {
    message: string;
    error?: Error;

    [key: string]: unknown;
}

interface BpmnCanvas {
    zoom(type: string, center?: string): void;

    addMarker(elementId: string, markerClass: string): void;

    removeMarker(elementId: string, markerClass: string): void;
}

interface BpmnElement {
    id?: string;

    [key: string]: unknown;
}

interface BpmnElementRegistry {
    getAll(): BpmnElement[];
}

declare module "bpmn-js/dist/bpmn-navigated-viewer.production.min.js" {
    class BpmnJS {
        constructor(options: { container: HTMLElement });

        destroy(): void;

        importXML(xml: string): Promise<{ warnings: BpmnWarning[] }>;

        get(service: "canvas"): BpmnCanvas;
        get(service: "elementRegistry"): BpmnElementRegistry;
        get(service: string): unknown;

        saveSVG(): Promise<{ svg: string }>
    }

    export = BpmnJS;
}
