package com.dramaflow.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

public class WatchRecordRequest {

    @Min(0) @Max(100)
    private double progress;

    @Min(0)
    private double lastPosition;

    private boolean completed;

    public double getProgress() { return progress; }
    public void setProgress(double progress) { this.progress = progress; }
    public double getLastPosition() { return lastPosition; }
    public void setLastPosition(double lastPosition) { this.lastPosition = lastPosition; }
    public boolean isCompleted() { return completed; }
    public void setCompleted(boolean completed) { this.completed = completed; }
}
