package com.example.port_health;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class SignupActivity extends AppCompatActivity {
    private EditText editTextName, editTextSurname, editTextPhone, editTextEmail, editTextPassword;
    private AutoCompleteTextView autoCompleteTextView; // Only dropdown we're using
    private Button buttonSubmit;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_signup);  // Only call once

        // Initialize the Material dropdown (AutoCompleteTextView)
        autoCompleteTextView = findViewById(R.id.autoCompleteTextView);

        // Create adapter from resource array (with default empty option)
        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(this,
                R.array.options_array, android.R.layout.simple_dropdown_item_1line);
        autoCompleteTextView.setAdapter(adapter);

        // Initialize other views from the layout
        editTextName = findViewById(R.id.editTextName);
        editTextSurname = findViewById(R.id.editTextSurname);
        editTextPhone = findViewById(R.id.editTextPhone);
        editTextEmail = findViewById(R.id.editTextEmail);
        editTextPassword = findViewById(R.id.editTextPassword);
        buttonSubmit = findViewById(R.id.buttonSubmit);

        buttonSubmit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String name = editTextName.getText().toString().trim();
                String surname = editTextSurname.getText().toString().trim();
                String phone = editTextPhone.getText().toString().trim();
                String email = editTextEmail.getText().toString().trim();
                String password = editTextPassword.getText().toString().trim();
                String selectedOption = autoCompleteTextView.getText().toString().trim();

                if (name.isEmpty() || surname.isEmpty() || phone.isEmpty() ||
                        email.isEmpty() || password.isEmpty() || selectedOption.isEmpty()) {
                    Toast.makeText(SignupActivity.this, "Please fill in all fields", Toast.LENGTH_SHORT).show();
                } else {
                    Log.d("SIGNUP_DEBUG", "Selected Option: " + selectedOption);
                    Toast.makeText(SignupActivity.this, "Sign up Successful! Please login.", Toast.LENGTH_SHORT).show();
                    Log.d("SIGNUP_DEBUG", "Redirecting to MoreInfoActivity");
                    Intent intent = new Intent(getApplicationContext(), MoreInfoActivity.class);
                    startActivity(intent);
                    finish();
                }
            }
        });
    }
}
