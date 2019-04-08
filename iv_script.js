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
    // Filters all the issues for self-made issues
    checkbox = document.getElementById("self-made-cb")
    result_set = [];
        
    if (checkbox.checked) {    
        issue_data.forEach(issue => {
            if (issue.self_made == true) {
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

// Search for domains
function search_domain() {
    var text = document.getElementById("domain-search-bar").value;
    if (text === "") {
        remove_filter();
    } else {
        filter_domain(text);
    }
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

// Search for user data
function search_user() {
    var text = document.getElementById("user-search-bar").value;
    if (text === "") {
        remove_filter();
    } else {
        filter_user(text);
    }
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

// Search for words in comment
function search_comment () {
    var text = document.getElementById("comment-search-bar").value;
    if (text === "") {
        remove_filter();
    } else {
        filter_comment(text);
    }
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

// Fetches the current issues from a json
fetch('./issues.json')
  .then(response => {
    return response.json()
  })
  .then(data => {
    // Work with JSON data here
    issue_data = data.issues;
    var list = document.getElementById("main-list");

    load_all_issues();

    // Fill issue count and date field
    document.getElementById("issue-count").innerText = data.issues.length;
    var date = new Date(data.date * 1000);
    var date_str = ("0" + date.getUTCDate()).slice(-2) + "." +
                   ("0" + (date.getUTCMonth() + 1)).slice(-2) + "." +
                   date.getUTCFullYear() + " " +
                   ("0" + date.getUTCHours()).slice(-2) + ":" +
                   ("0" + date.getUTCMinutes()).slice(-2) + " UTC+2";

    document.getElementById("issues-date").innerText = date_str;
  })
  .catch(err => {
    // Do something for an error here
    console.error(err);
  })
