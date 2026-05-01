package com.dramaflow.service;

import com.dramaflow.dto.*;
import com.dramaflow.model.User;
import com.dramaflow.repository.UserRepository;
import com.dramaflow.security.JwtUtil;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    public AuthService(UserRepository userRepository, PasswordEncoder passwordEncoder, JwtUtil jwtUtil) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtil = jwtUtil;
    }

    public UserResponse register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "邮箱已被注册");
        }

        User user = new User();
        user.setNickname(request.getNickname());
        user.setEmail(request.getEmail());
        user.setHashedPassword(passwordEncoder.encode(request.getPassword()));
        userRepository.save(user);

        return new UserResponse(user.getId(), user.getNickname(), user.getEmail());
    }

    public TokenResponse login(LoginRequest request) {
        User user = userRepository.findByEmail(request.getEmail()).orElse(null);
        if (user == null || !passwordEncoder.matches(request.getPassword(), user.getHashedPassword())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "邮箱或密码错误");
        }

        String accessToken = jwtUtil.createAccessToken(user.getId());
        String refreshToken = jwtUtil.createRefreshToken(user.getId());
        UserResponse userResp = new UserResponse(user.getId(), user.getNickname(), user.getEmail());

        return new TokenResponse(accessToken, refreshToken, userResp);
    }

    public TokenResponse refresh(RefreshTokenRequest request) {
        String type;
        Integer userId;
        try {
            type = jwtUtil.parseToken(request.getRefreshToken()).get("type", String.class);
            userId = jwtUtil.getUserIdFromToken(request.getRefreshToken());
        } catch (Exception e) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Refresh token 无效");
        }

        if (!"refresh".equals(type)) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Refresh token 类型错误");
        }

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "用户不存在"));

        String newAccess = jwtUtil.createAccessToken(user.getId());
        String newRefresh = jwtUtil.createRefreshToken(user.getId());
        UserResponse userResp = new UserResponse(user.getId(), user.getNickname(), user.getEmail());

        return new TokenResponse(newAccess, newRefresh, userResp);
    }
}
