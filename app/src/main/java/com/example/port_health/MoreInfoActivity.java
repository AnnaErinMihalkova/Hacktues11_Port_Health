package com.example.port_health;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;


public class MoreInfoActivity extends AppCompatActivity {
    private EditText editTextGender, editTextWeight, editTextAge, editTextHeight, editTextAllergies, editTextDiet;
    private Button buttonSubmit;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_moreinfo);


        editTextGender = findViewById(R.id.editTextGender);
        editTextWeight = findViewById(R.id.editTextWeight);
        editTextAge = findViewById(R.id.editTextAge);
        editTextHeight = findViewById(R.id.editTextHeight);
        editTextAllergies = findViewById(R.id.editTextAllergies);
        editTextDiet = findViewById(R.id.editTextDiet);
        buttonSubmit = findViewById(R.id.buttonSubmit);

        buttonSubmit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String gender = editTextGender.getText().toString().trim();
                String weight = editTextWeight.getText().toString().trim();
                String age = editTextAge.getText().toString().trim();
                String height = editTextHeight.getText().toString().trim();
                String allergies = editTextAllergies.getText().toString().trim();
                String diet = editTextDiet.getText().toString().trim();

                if (gender.isEmpty() || weight.isEmpty() || age.isEmpty() || height.isEmpty() || allergies.isEmpty() || diet.isEmpty())  {
                    Toast.makeText(MoreInfoActivity.this, "Please fill in all fields", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(MoreInfoActivity.this, "Sign up Successful!", Toast.LENGTH_SHORT).show();
                    Intent intent = new Intent(MoreInfoActivity.this, MainActivity.class);
                    startActivity(intent);
                }
            }
        });
    }


}
