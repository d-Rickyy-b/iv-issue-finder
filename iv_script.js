function create_issue(issue_url, domain_name, author_name, creator_name, comment, reply) {
    let html = `<div class="list-item">
                    <div class="domain">
                    <a href="${issue_url}" style="font-weight:bold">${domain_name}</a>
                    </div>
                    <div class="issue-author name">${author_name}</div>
                    <div class="template-creator name">${creator_name}</div>
                    <div class="comment-box">
                        <div class="issue-comment comment-field">${comment}</div>
                        <div class="issue-reply comment-field">${reply}</div>
                    </div>
                </div>`

    return html;
}

function filter_self_made() {
    checkbox = document.getElementById("self-made-cb")
    result_set = [];
        
    if (checkbox.checked) {    
        issue_data.forEach(issue => {
            if (issue.template_creator == issue.author) {
                result_set.push(issue);
            }
        });
        draw_result_set();
    } else {
        remove_filter();
        load_all_issues();
    }
}

function filter_no_reply() {
    checkbox = document.getElementById("reply-cb")
    result_set = [];
    
    if (checkbox.checked) {    
        issue_data.forEach(issue => {
            if (issue.creator_comment == "") {
                result_set.push(issue);
            }    
        });
        draw_result_set();
    } else {
        remove_filter();
        load_all_issues();
    }
}

function load_all_issues() {
    list = document.getElementById("main-list");
    list.innerHTML = "";
    result_set = [];

    issue_data.forEach(issue => {
        result_set.push(issue);
    });
    draw_result_set();
}

function filter_domain(name) {
    list = document.getElementById("main-list");
    result_set = [];

    issue_data.forEach(issue => {
        var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
        var domain_name = regExp.exec(issue.url)[1]
        if (domain_name.includes(String(name))) {
            result_set.push(issue);
        }
    });
    draw_result_set();
}

function filter_user(name) {
    result_set = [];

    issue_data.forEach(issue => {
        if (issue.author.includes(String(name)) || issue.template_creator.includes(String(name))) {
            result_set.push(issue);
        }
    });
    draw_result_set();
}

function filter_comment(text) {
    result_set = [];

    issue_data.forEach(issue => {
        if (issue.comment.includes(String(text)) || issue.creator_comment.includes(String(text))) {
            result_set.push(issue);
        }
    });
    draw_result_set();
}

function search_user() {
    var text = document.getElementById("user-search-bar").value;
    if (text === "") {
        remove_filter();
    } else {
        filter_user(text);
    }
}

function search_comment () {
    var text = document.getElementById("comment-search-bar").value;
    if (text === "") {
        remove_filter();
    } else {
        filter_comment(text);
    }
}

function remove_filter() {
    result_set = [];
    issue_checkbox = document.getElementById("self-made-cb");
    issue_checkbox.checked = false;

    domain_search_field = document.getElementById("domain-search-bar");
    domain_search_field.value = "";

    user_search_field = document.getElementById("user-search-bar");
    user_search_field.value = "";

    comment_search_field = document.getElementById("comment-search-bar");
    comment_search_field.value = "";
    load_all_issues();
}

function search_domain() {
    var text = document.getElementById("domain-search-bar").value;
    if (text === "") {
        remove_filter();
    } else {
        filter_domain(text);
    }
}

function draw_result_set() {
    // Draws the current result_set
    list = document.getElementById("main-list");
    let html = "";

    result_set.forEach(issue => {
        var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
        var domain_name = regExp.exec(issue.url)[1]
        if (issue.author.includes(String(name)) || issue.template_creator.includes(String(name))) {
            html += create_issue(issue.url, domain_name, issue.author, issue.template_creator, issue.comment, issue.creator_comment);
        }
    });
    list.innerHTML = html;

    result_set_counter = document.getElementById("result-set-counter").innerText = result_set.length;
}

var issue_data = [];
var result_set = [];

// ./domains.json
fetch('./issues.json')
  .then(response => {
    return response.json()
  })
  .then(data => {
    // Work with JSON data here
    issue_data = data.issues;
    var list = document.getElementById("main-list");

    load_all_issues();

  })
  .catch(err => {
    // Do something for an error here
    console.error(err);
  })
