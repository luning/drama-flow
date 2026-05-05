package com.dramaflow.auth.ui

import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.dramaflow.R
import com.dramaflow.auth.viewmodel.AuthState
import com.dramaflow.auth.viewmodel.AuthViewModel
import com.dramaflow.databinding.FragmentLoginBinding

class LoginFragment : Fragment(R.layout.fragment_login) {

    private var _binding: FragmentLoginBinding? = null
    private val binding get() = _binding!!
    private val viewModel: AuthViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentLoginBinding.bind(view)

        // AC-USER-10: 勾选"记住我"后重启 App 自动登录
        viewModel.tryAutoLogin()

        binding.btnLogin.setOnClickListener {
            val email = binding.etEmail.text.toString()
            val password = binding.etPassword.text.toString()
            val remember = binding.cbRemember.isChecked
            viewModel.login(email, password, remember)
        }

        binding.tvRegister.setOnClickListener {
            findNavController().navigate(R.id.action_login_to_register)
        }

        viewModel.loginState.observe(viewLifecycleOwner) { state ->
            when (state) {
                is AuthState.Loading -> {
                    binding.btnLogin.isEnabled = false
                    binding.tvError.visibility = View.GONE
                }
                is AuthState.Success -> {
                    binding.tvError.visibility = View.GONE
                    findNavController().navigate(R.id.action_login_to_home)
                }
                is AuthState.Error -> {
                    binding.btnLogin.isEnabled = true
                    binding.tvError.text = state.message
                    binding.tvError.visibility = View.VISIBLE
                }
                else -> {
                    binding.btnLogin.isEnabled = true
                    binding.tvError.visibility = View.GONE
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
