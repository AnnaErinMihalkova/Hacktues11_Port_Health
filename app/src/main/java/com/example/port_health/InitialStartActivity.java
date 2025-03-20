package com.example.port_health;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import androidx.appcompat.app.AppCompatActivity;

public class InitialStartActivity extends AppCompatActivity {
    private Button buttonLogIn;
    private Button buttonSignUp;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_initial_start); // ✅ Ensure the correct layout is used

        buttonLogIn = findViewById(R.id.buttonLogIn);
        buttonSignUp = findViewById(R.id.buttonSignUp);

        // Navigate to LoginActivity when "Log In" is clicked
        buttonLogIn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(InitialStartActivity.this, LoginActivity.class);
                startActivity(intent);
            }
        });

        // Navigate to SignupActivity when "Sign Up" is clicked
        buttonSignUp.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(InitialStartActivity.this, SignupActivity.class);
                startActivity(intent);
            }
        });
    }
}
