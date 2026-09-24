# MCP College Assistant

An AI-powered college assistant built using the Model Context Protocol (MCP).

This project demonstrates how an AI application can communicate with an MCP server to access college information through resources and perform actions through MCP tools.

## Features

- MCP client-server communication
- MCP resource discovery and access
- MCP tool discovery and execution
- OpenAI API integration
- College department and course information
- Task management
- STDIO transport
- JSON-based data storage

## Architecture

```text
User
 |
 v
AI Application
 |
 v
MCP Client
 |
 v
MCP Server
 |-------------------|
 |                   |
 v                   v
Resources           Tools
 |                   |
 v                   v
College Data       Task Management
 |                   |
 |---------+---------|
           |
           v
         Result
           |
           v
    AI Final Response