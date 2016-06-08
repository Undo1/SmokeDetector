# -*- coding: utf-8 -*-
import regex
import requests

class FindSpam:
    @staticmethod
    def test_post(title, body, user_name, site, is_answer, body_is_summary, user_rep, post_score):
        print title
        print site
        if site == 'stackoverflow.com':
          response = requests.get("http://localhost:8000/?q=" + title)
          print response.text

        return [], ""

