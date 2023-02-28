/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export type FileEdit = FileEdit1;
export type Filepath = string;
export type Line = number;
export type Character = number;
export type Replacement = string;

export interface FileEdit1 {
  filepath: Filepath;
  range: Range;
  replacement: Replacement;
}
/**
 * A range in a file. 0-indexed.
 */
export interface Range {
  start: Position;
  end: Position;
}
export interface Position {
  line: Line;
  character: Character;
}
