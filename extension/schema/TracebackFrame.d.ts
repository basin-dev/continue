/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export type TracebackFrame = TracebackFrame1;
export type Filepath = string;
export type Lineno = number;
export type Function = string;
export type Code = string;

export interface TracebackFrame1 {
  filepath: Filepath;
  lineno: Lineno;
  function: Function;
  code?: Code;
}
