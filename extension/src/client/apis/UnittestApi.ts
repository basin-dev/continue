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
  FailingTestBody,
  FilePosition,
  HTTPValidationError,
} from '../models';
import {
    FailingTestBodyFromJSON,
    FailingTestBodyToJSON,
    FilePositionFromJSON,
    FilePositionToJSON,
    HTTPValidationErrorFromJSON,
    HTTPValidationErrorToJSON,
} from '../models';

export interface FailingtestUnittestFailingtestPostRequest {
    failingTestBody: FailingTestBody;
}

export interface ForlineUnittestForlinePostRequest {
    userid: string;
    filePosition: FilePosition;
}

/**
 * 
 */
export class UnittestApi extends runtime.BaseAPI {

    /**
     * Write a failing test for the function encapsulating the given line number.
     * Failingtest
     */
    async failingtestUnittestFailingtestPostRaw(requestParameters: FailingtestUnittestFailingtestPostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.failingTestBody === null || requestParameters.failingTestBody === undefined) {
            throw new runtime.RequiredError('failingTestBody','Required parameter requestParameters.failingTestBody was null or undefined when calling failingtestUnittestFailingtestPost.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        const response = await this.request({
            path: `/unittest/failingtest`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: FailingTestBodyToJSON(requestParameters.failingTestBody),
        }, initOverrides);

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Write a failing test for the function encapsulating the given line number.
     * Failingtest
     */
    async failingtestUnittestFailingtestPost(requestParameters: FailingtestUnittestFailingtestPostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<any> {
        const response = await this.failingtestUnittestFailingtestPostRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     * Write unit test for the function encapsulating the given line number.
     * Forline
     */
    async forlineUnittestForlinePostRaw(requestParameters: ForlineUnittestForlinePostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.userid === null || requestParameters.userid === undefined) {
            throw new runtime.RequiredError('userid','Required parameter requestParameters.userid was null or undefined when calling forlineUnittestForlinePost.');
        }

        if (requestParameters.filePosition === null || requestParameters.filePosition === undefined) {
            throw new runtime.RequiredError('filePosition','Required parameter requestParameters.filePosition was null or undefined when calling forlineUnittestForlinePost.');
        }

        const queryParameters: any = {};

        if (requestParameters.userid !== undefined) {
            queryParameters['userid'] = requestParameters.userid;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        const response = await this.request({
            path: `/unittest/forline`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: FilePositionToJSON(requestParameters.filePosition),
        }, initOverrides);

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Write unit test for the function encapsulating the given line number.
     * Forline
     */
    async forlineUnittestForlinePost(requestParameters: ForlineUnittestForlinePostRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<any> {
        const response = await this.forlineUnittestForlinePostRaw(requestParameters, initOverrides);
        return await response.value();
    }

}
