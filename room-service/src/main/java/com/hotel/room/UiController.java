package com.hotel.room;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

/** Stable entry points for the UI packaged in this service. */
@Controller
public class UiController {
    @GetMapping({"/ui", "/ui/"})
    public String ui() {
        return "redirect:/ui/index.html";
    }
}
