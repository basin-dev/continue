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
import type { RangeInFile } from './RangeInFile';
import {
    RangeInFileFromJSON,
    RangeInFileFromJSONTyped,
    RangeInFileToJSON,
} from './RangeInFile';

/**
 * 
 * @export
 * @interface FindResp
 */
export interface FindResp {
    /**
     * 
     * @type {Array<RangeInFile>}
     * @memberof FindResp
     */
    response: Array<RangeInFile>;
}

/**
 * Check if a given object implements the FindResp interface.
 */
export function instanceOfFindResp(value: object): boolean {
    let isInstance = true;
    isInstance = isInstance && "response" in value;

    return isInstance;
}

export function FindRespFromJSON(json: any): FindResp {
    return FindRespFromJSONTyped(json, false);
}

export function FindRespFromJSONTyped(json: any, ignoreDiscriminator: boolean): FindResp {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'response': ((json['response'] as Array<any>).map(RangeInFileFromJSON)),
    };
}

export function FindRespToJSON(value?: FindResp | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'response': ((value.response as Array<any>).map(RangeInFileToJSON)),
    };
}

