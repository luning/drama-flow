package com.dramaflow.exception;

public class ErrorResponse {
    private String detail;
    private int code;
    private String path;

    public ErrorResponse(String detail, int code, String path) {
        this.detail = detail;
        this.code = code;
        this.path = path;
    }

    public String getDetail() { return detail; }
    public int getCode() { return code; }
    public String getPath() { return path; }
}
