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

import { exists, mapValues } from '../runtime';
/**
 * 
 * @export
 * @interface CompletionResponse
 */
export interface CompletionResponse {
    /**
     * 
     * @type {string}
     * @memberof CompletionResponse
     */
    completion: string;
}

/**
 * Check if a given object implements the CompletionResponse interface.
 */
export function instanceOfCompletionResponse(value: object): boolean {
    let isInstance = true;
    isInstance = isInstance && "completion" in value;

    return isInstance;
}

export function CompletionResponseFromJSON(json: any): CompletionResponse {
    return CompletionResponseFromJSONTyped(json, false);
}

export function CompletionResponseFromJSONTyped(json: any, ignoreDiscriminator: boolean): CompletionResponse {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'completion': json['completion'],
    };
}

export function CompletionResponseToJSON(value?: CompletionResponse | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'completion': value.completion,
    };
}

