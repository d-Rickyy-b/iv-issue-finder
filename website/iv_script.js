function create_issue(issue_url, domain_name, author_name, creator_name, comment, reply, status) {
    switch (status) {
        case 0:
            status = "unhandled";
            text = "Unhandled";
            break;
        case 1:
            status = "accepted";
            text = "Accepted";
            break;
        case 2:
            status = "declined";
            text = "Declined";
            break;
        default:
            status = "unhandled";
            text = "Unhandled";
    }
    
    let html = `<div class="list-item">
                    <div class="domain">
                        <a href="${issue_url}">${domain_name}</a>
                        <div class="status ${status}">${text}</div>
                    </div>
                    <div class="author-box">
                        <div class="issue-author name">${author_name}</div>
                        <div class="template-creator name">${creator_name}</div>
                    </div>
                    <div class="comment-box">
                        <div class="issue-comment comment-field">${comment}</div>
                        <div class="issue-reply comment-field">${reply}</div>
                    </div>
                </div>`

    return html;
}

function get_domain_from_url(issue) {
    var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
    var domain_name = regExp.exec(issue.url)[1];
    return domain_name;
}

function filter() {
    // Get all filters
    self_made_cb = document.getElementById("self-made-cb");
    no_self_made_cb = document.getElementById("no-self-made-cb");
    no_reply_cb = document.getElementById("no-reply-cb");
    with_reply_cb = document.getElementById("with-reply-cb");

    only_unhandled_cb = document.getElementById("only-unhandled-cb");
    only_accepted_cb = document.getElementById("only-accepted-cb");
    only_declined_cb = document.getElementById("only-declined-cb");

    var domain_search = document.getElementById("domain-search-bar").value;
    var user_search = document.getElementById("user-search-bar").value;
    var comment_search = document.getElementById("comment-search-bar").value;

    ret_result_set = [...issue_data];

    // Check for self-made issues
    if (self_made_cb.checked) {
        no_self_made_cb.checked = false;
        no_self_made_cb.disabled = true;
        tmp_result_set = [];
        ret_result_set.forEach(issue => {
            if (issue.self_made == true) {
                tmp_result_set.push(issue);
            }
        });
        ret_result_set = [...tmp_result_set];
    } else {
        no_self_made_cb.disabled = false;
    }
    
    // Check for non-self-made issues
    if (no_self_made_cb.checked) {
        self_made_cb.checked = false;
        self_made_cb.disabled = true;
        tmp_result_set = [];
        ret_result_set.forEach(issue => {
            if (issue.self_made == false) {
                tmp_result_set.push(issue);
            }
        });
        ret_result_set = [...tmp_result_set];
    } else {
        self_made_cb.disabled = false;
    }

    // Check issues without reply
    if (no_reply_cb.checked) {
        with_reply_cb.checked = false;
        with_reply_cb.disabled = true;
        tmp_result_set = [];
        ret_result_set.forEach(issue => {
            if (issue.creator_comment == "") {
                tmp_result_set.push(issue);
            }    
        });
        ret_result_set = [...tmp_result_set];
    } else {
        with_reply_cb.disabled = false;
    }
    
    // Check issues with reply
    if (with_reply_cb.checked) {
        no_reply_cb.checked = false;
        no_reply_cb.disabled = true;
        tmp_result_set = [];
        ret_result_set.forEach(issue => {
            if (issue.creator_comment != "") {
                tmp_result_set.push(issue);
            }    
        });
        ret_result_set = [...tmp_result_set];
    } else {
        no_reply_cb.disabled = false;
    }

    var cbs = [only_unhandled_cb, only_accepted_cb, only_declined_cb];
    
    if (only_unhandled_cb.checked == false && only_accepted_cb.checked == false && only_declined_cb.checked == false) {
        only_unhandled_cb.disabled = false;
        only_accepted_cb.disabled = false;
        only_declined_cb.disabled = false;
    } else {
        cbs.forEach(cb => {
            if (cb.checked) {
                var tmp = [...cbs];
                var index = cbs.indexOf(cb);
                tmp.splice(index, 1);
                tmp.forEach(c => {
                    console.log(c);
                    c.checked = false;
                    c.disabled = true;
                });
            }
        });
    }

    // Check unhandled issues
    if (only_unhandled_cb.checked) {        
        tmp_result_set = [];
        ret_result_set.forEach(issue => {
            if (issue.status == 0) {
                tmp_result_set.push(issue);
            }    
        });
        ret_result_set = [...tmp_result_set];
    }

    // Check accepted issues
    if (only_accepted_cb.checked) {        
        tmp_result_set = [];
        ret_result_set.forEach(issue => {
            if (issue.status == 1) {
                tmp_result_set.push(issue);
            }    
        });
        ret_result_set = [...tmp_result_set];
    }

    // Check declined issues
    if (only_declined_cb.checked) {
        tmp_result_set = [];
        ret_result_set.forEach(issue => {
            if (issue.status == 2) {
                tmp_result_set.push(issue);
            }    
        });
        ret_result_set = [...tmp_result_set];
    }

    if (domain_search != "") {
        tmp_result_set = [];
        ret_result_set.forEach(issue => {
            domain = issue.domain;
            if (domain == undefined) {
                domain=get_domain_from_url(issue);
            }

            if (domain.toLowerCase().includes(String(domain_search).toLowerCase())) {
                tmp_result_set.push(issue);
            }
        });
        ret_result_set = [...tmp_result_set];
    }

    if (user_search != "") {
        console.log("Test");
        tmp_result_set = [];
        ret_result_set.forEach(issue => {
            if (issue.author.toLowerCase().includes(String(user_search).toLowerCase()) || issue.template_creator.toLowerCase().includes(String(user_search).toLowerCase())) {
                tmp_result_set.push(issue);
            }
        });
        ret_result_set = [...tmp_result_set];
    }

    if (comment_search != "") {
        tmp_result_set = [];
        ret_result_set.forEach(issue => {
            if (issue.comment.toLowerCase().includes(String(comment_search).toLowerCase()) || issue.creator_comment.toLowerCase().includes(String(comment_search).toLowerCase())) {
                tmp_result_set.push(issue);
            }
        });
        ret_result_set = [...tmp_result_set];
    }

    result_set = [...ret_result_set];
    draw_result_set();
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

function remove_filter() {
    result_set = [];
    issue_checkbox = document.getElementById("self-made-cb");
    issue_checkbox.checked = false;

    reply_checkbox = document.getElementById("no-reply-cb");
    reply_checkbox.checked = false;

    reply_checkbox = document.getElementById("with-reply-cb");
    reply_checkbox.checked = false;

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
        domain = issue.domain;
        if (domain == undefined) {
            domain=get_domain_from_url(issue);
        }

        if (issue.author.includes(String(name)) || issue.template_creator.includes(String(name))) {
            html += create_issue(issue.url, domain, issue.author, issue.template_creator, issue.comment, issue.creator_comment, issue.status);
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

    load_all_issues();

    // Fill issue count and date field
    document.getElementById("issue-count").innerText = data.issues.length;
    var date = new Date(data.date * 1000);
    var date_str = ("0" + date.getUTCDate()).slice(-2) + "." +
                   ("0" + (date.getUTCMonth() + 1)).slice(-2) + "." +
                   date.getUTCFullYear() + " " +
                   ("0" + date.getUTCHours()).slice(-2) + ":" +
                   ("0" + date.getUTCMinutes()).slice(-2) + " UTC";

    document.getElementById("issues-date").innerText = date_str;
  })
  .catch(err => {
    // Do something for an error here
    console.error(err);
  })
