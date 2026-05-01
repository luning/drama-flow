package com.dramaflow.dto;

public class UserResponse {
    private Integer id;
    private String nickname;
    private String email;

    public UserResponse(Integer id, String nickname, String email) {
        this.id = id;
        this.nickname = nickname;
        this.email = email;
    }

    public Integer getId() { return id; }
    public String getNickname() { return nickname; }
    public String getEmail() { return email; }
}
