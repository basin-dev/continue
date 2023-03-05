/* tslint:disable */
/* eslint-disable */
/**
 * Continue API
 * Continue API
 *
 * The version of the OpenAPI document: 1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


import * as runtime from '../runtime';
import type {
  CompletionResponse,
  EditResp,
  ExplainResponse,
  FindBody,
  FindResp,
  HTTPValidationError,
  InlineBody,
  SerializedDebugContext,
  Traceback,
} from '../models';
import {
    CompletionResponseFromJSON,
    CompletionResponseToJSON,
    EditRespFromJSON,
    EditRespToJSON,
    ExplainResponseFromJSON,
    ExplainResponseToJSON,
    FindBodyFromJSON,
    FindBodyToJSON,
    FindRespFromJSON,
    FindRespToJSON,
    HTTPValidationErrorFromJSON,
    HTTPValidationErrorToJSON,
    InlineBodyFromJSON,
    InlineBodyToJSON,
    SerializedDebugContextFromJSON,
    SerializedDebugContextToJSON,
    TracebackFromJSON,
    TracebackToJSON,
} from '../models';

export interface EditEndpointDebugEditPostRequest {
    serializedDebugContext: SerializedDebugContext;
    xVscMachineId?: string;
}

export interface ExplainDebugExplainPostRequest {
    serializedDebugContext: SerializedDebugContext;
    xVscMachineId?: string;
}

export interface FindDocsDebugFindDocsGetRequest {
    traceback: string;
}

export interface FindSusCodeEndpointDebugFindPostRequest {
    findBody: FindBody;
}

export interface InlineDebugInlinePostRequest {
    inlineBody: InlineBody;
}

export interface ListtenDebugListPostRequest {
    serializedDebugContext: SerializedDebugContext;
    xVscMachineId?: string;
}

export interface ParseTracebackEndpointDebugParseTracebackGetRequest {
    traceback: string;
}

export interface RunDebugRunPostRequest {
    filepath: string;
    makeEdit?: boolean;
}

export interface SuggestionDebugSuggestionGetRequest {
    traceback: string;
}

/**
 * 
 */
export class DebugApi extends runtime.BaseAPI {

    /**
     * Edit Endpoint
     */
    async editEndpointDebugEditPostRaw(requestParameters: EditEndpointDebugEditPostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<EditResp>> {
        if (requestParameters.serializedDebugContext === null || requestParameters.serializedDebugContext === undefined) {
            throw new runtime.RequiredError('serializedDebugContext','Required parameter requestParameters.serializedDebugContext was null or undefined when calling editEndpointDebugEditPost.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        if (requestParameters.xVscMachineId !== undefined && requestParameters.xVscMachineId !== null) {
            headerParameters['x-vsc-machine-id'] = String(requestParameters.xVscMachineId);
        }

        const response = await this.request({
            path: `/debug/edit`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: SerializedDebugContextToJSON(requestParameters.serializedDebugContext),
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => EditRespFromJSON(jsonValue));
    }

    /**
     * Edit Endpoint
     */
    async editEndpointDebugEditPost(requestParameters: EditEndpointDebugEditPostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<EditResp> {
        const response = await this.editEndpointDebugEditPostRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Explain
     */
    async explainDebugExplainPostRaw(requestParameters: ExplainDebugExplainPostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<ExplainResponse>> {
        if (requestParameters.serializedDebugContext === null || requestParameters.serializedDebugContext === undefined) {
            throw new runtime.RequiredError('serializedDebugContext','Required parameter requestParameters.serializedDebugContext was null or undefined when calling explainDebugExplainPost.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        if (requestParameters.xVscMachineId !== undefined && requestParameters.xVscMachineId !== null) {
            headerParameters['x-vsc-machine-id'] = String(requestParameters.xVscMachineId);
        }

        const response = await this.request({
            path: `/debug/explain`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: SerializedDebugContextToJSON(requestParameters.serializedDebugContext),
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => ExplainResponseFromJSON(jsonValue));
    }

    /**
     * Explain
     */
    async explainDebugExplainPost(requestParameters: ExplainDebugExplainPostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<ExplainResponse> {
        const response = await this.explainDebugExplainPostRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Find Docs
     */
    async findDocsDebugFindDocsGetRaw(requestParameters: FindDocsDebugFindDocsGetRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<CompletionResponse>> {
        if (requestParameters.traceback === null || requestParameters.traceback === undefined) {
            throw new runtime.RequiredError('traceback','Required parameter requestParameters.traceback was null or undefined when calling findDocsDebugFindDocsGet.');
        }

        const queryParameters: any = {};

        if (requestParameters.traceback !== undefined) {
            queryParameters['traceback'] = requestParameters.traceback;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/debug/find_docs`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => CompletionResponseFromJSON(jsonValue));
    }

    /**
     * Find Docs
     */
    async findDocsDebugFindDocsGet(requestParameters: FindDocsDebugFindDocsGetRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<CompletionResponse> {
        const response = await this.findDocsDebugFindDocsGetRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Find Sus Code Endpoint
     */
    async findSusCodeEndpointDebugFindPostRaw(requestParameters: FindSusCodeEndpointDebugFindPostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<FindResp>> {
        if (requestParameters.findBody === null || requestParameters.findBody === undefined) {
            throw new runtime.RequiredError('findBody','Required parameter requestParameters.findBody was null or undefined when calling findSusCodeEndpointDebugFindPost.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        const response = await this.request({
            path: `/debug/find`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: FindBodyToJSON(requestParameters.findBody),
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => FindRespFromJSON(jsonValue));
    }

    /**
     * Find Sus Code Endpoint
     */
    async findSusCodeEndpointDebugFindPost(requestParameters: FindSusCodeEndpointDebugFindPostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<FindResp> {
        const response = await this.findSusCodeEndpointDebugFindPostRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Inline
     */
    async inlineDebugInlinePostRaw(requestParameters: InlineDebugInlinePostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<CompletionResponse>> {
        if (requestParameters.inlineBody === null || requestParameters.inlineBody === undefined) {
            throw new runtime.RequiredError('inlineBody','Required parameter requestParameters.inlineBody was null or undefined when calling inlineDebugInlinePost.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        const response = await this.request({
            path: `/debug/inline`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: InlineBodyToJSON(requestParameters.inlineBody),
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => CompletionResponseFromJSON(jsonValue));
    }

    /**
     * Inline
     */
    async inlineDebugInlinePost(requestParameters: InlineDebugInlinePostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<CompletionResponse> {
        const response = await this.inlineDebugInlinePostRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Listten
     */
    async listtenDebugListPostRaw(requestParameters: ListtenDebugListPostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<CompletionResponse>> {
        if (requestParameters.serializedDebugContext === null || requestParameters.serializedDebugContext === undefined) {
            throw new runtime.RequiredError('serializedDebugContext','Required parameter requestParameters.serializedDebugContext was null or undefined when calling listtenDebugListPost.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        if (requestParameters.xVscMachineId !== undefined && requestParameters.xVscMachineId !== null) {
            headerParameters['x-vsc-machine-id'] = String(requestParameters.xVscMachineId);
        }

        const response = await this.request({
            path: `/debug/list`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: SerializedDebugContextToJSON(requestParameters.serializedDebugContext),
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => CompletionResponseFromJSON(jsonValue));
    }

    /**
     * Listten
     */
    async listtenDebugListPost(requestParameters: ListtenDebugListPostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<CompletionResponse> {
        const response = await this.listtenDebugListPostRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Parse Traceback Endpoint
     */
    async parseTracebackEndpointDebugParseTracebackGetRaw(requestParameters: ParseTracebackEndpointDebugParseTracebackGetRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<Traceback>> {
        if (requestParameters.traceback === null || requestParameters.traceback === undefined) {
            throw new runtime.RequiredError('traceback','Required parameter requestParameters.traceback was null or undefined when calling parseTracebackEndpointDebugParseTracebackGet.');
        }

        const queryParameters: any = {};

        if (requestParameters.traceback !== undefined) {
            queryParameters['traceback'] = requestParameters.traceback;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/debug/parse_traceback`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => TracebackFromJSON(jsonValue));
    }

    /**
     * Parse Traceback Endpoint
     */
    async parseTracebackEndpointDebugParseTracebackGet(requestParameters: ParseTracebackEndpointDebugParseTracebackGetRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<Traceback> {
        const response = await this.parseTracebackEndpointDebugParseTracebackGetRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Returns boolean indicating whether error was found, edited, and solved, or not all of these.
     * Run
     */
    async runDebugRunPostRaw(requestParameters: RunDebugRunPostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.filepath === null || requestParameters.filepath === undefined) {
            throw new runtime.RequiredError('filepath','Required parameter requestParameters.filepath was null or undefined when calling runDebugRunPost.');
        }

        const queryParameters: any = {};

        if (requestParameters.filepath !== undefined) {
            queryParameters['filepath'] = requestParameters.filepath;
        }

        if (requestParameters.makeEdit !== undefined) {
            queryParameters['make_edit'] = requestParameters.makeEdit;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/debug/run`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
        }, initOverrides);

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Returns boolean indicating whether error was found, edited, and solved, or not all of these.
     * Run
     */
    async runDebugRunPost(requestParameters: RunDebugRunPostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<any> {
        const response = await this.runDebugRunPostRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Suggestion
     */
    async suggestionDebugSuggestionGetRaw(requestParameters: SuggestionDebugSuggestionGetRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<CompletionResponse>> {
        if (requestParameters.traceback === null || requestParameters.traceback === undefined) {
            throw new runtime.RequiredError('traceback','Required parameter requestParameters.traceback was null or undefined when calling suggestionDebugSuggestionGet.');
        }

        const queryParameters: any = {};

        if (requestParameters.traceback !== undefined) {
            queryParameters['traceback'] = requestParameters.traceback;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/debug/suggestion`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => CompletionResponseFromJSON(jsonValue));
    }

    /**
     * Suggestion
     */
    async suggestionDebugSuggestionGet(requestParameters: SuggestionDebugSuggestionGetRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<CompletionResponse> {
        const response = await this.suggestionDebugSuggestionGetRaw(requestParameters, initOverrides);
        return await response.value();
    }

}
