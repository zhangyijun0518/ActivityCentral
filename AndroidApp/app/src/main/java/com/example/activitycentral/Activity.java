package com.example.activitycentral;

import java.util.List;

public class Activity {
    public String title;
    public String description;
    public String location;
    public String thumbnail;
    public List<String> images;

    public Activity(String title, String description, String location,
                    String thumbnail) {
        this.title = title;
        this.description = description;
        this.location = location;
        this.thumbnail = thumbnail;
    }
}
