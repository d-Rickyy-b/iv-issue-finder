function create_issue(issue_url, domain_name, author_name, creator_name, comment, reply) {
    var container = document.createElement('div');
    container.classList.add('list-item');

    container.innerHTML = `<div class="domain">
                                <a href="${issue_url}" style="font-weight:bold">${domain_name}</a>
                            </div>
                            <div class="issue-author name">${author_name}</div>
                            <div class="template-creator name">${creator_name}</div>
                            <div class="comment-box">
                                <div class="issue-comment comment-field">${comment}</div>
                                <div class="issue-reply comment-field">${reply}</div>
                            </div>`

    return container;
}

function filter_self_made() {
    checkbox = document.getElementById("self-made-cb")
    list = document.getElementById("main-list");
    list.innerHTML = "";
    
    if (checkbox.checked) {    
        for (i = 0; i < issue_data.length; i++) {
            var issue = issue_data[i];
            var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
            var domain_name = regExp.exec(issue.url)[1]
            if (issue.template_creator == issue.author) {
                var container = create_issue(issue.url, domain_name, issue.author, issue.template_creator, issue.comment, issue.creator_comment);
                list.appendChild(container);
            }
        }
    } else {
        load_all_issues();
    }
}

function filter_no_reply() {
    checkbox = document.getElementById("reply-cb")
    list = document.getElementById("main-list");
    list.innerHTML = "";
    
    if (checkbox.checked) {    
        for (i = 0; i < issue_data.length; i++) {
            var issue = issue_data[i];
            var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
            var domain_name = regExp.exec(issue.url)[1]
            if (issue.creator_comment == "") {
                var container = create_issue(issue.url, domain_name, issue.author, issue.template_creator, issue.comment, issue.creator_comment);
                list.appendChild(container);
            }
        }
    } else {
        load_all_issues();
    }
}

function load_all_issues() {
    list = document.getElementById("main-list");
    list.innerHTML = "";

    issue_data.forEach(issue => {              
        var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
        var container = create_issue(issue.url, regExp.exec(issue.url)[1], issue.author, issue.template_creator, issue.comment, issue.creator_comment);
        list.appendChild(container);
    });
}

function filter(name) {
    list = document.getElementById("main-list");
    list.innerHTML = "";

    for (i = 0; i < issue_data.length; i++) {
        var issue = issue_data[i];
        var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
        var domain_name = regExp.exec(issue.url)[1]
        if (domain_name.includes(String(name))) {
            var container = create_issue(issue.url, domain_name, issue.author, issue.template_creator, issue.comment, issue.creator_comment);
            list.appendChild(container);
        }
    }
}

function filter_user(name) {
    list = document.getElementById("main-list");
    list.innerHTML = "";

    for (i = 0; i < issue_data.length; i++) {
        var issue = issue_data[i];
        var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
        var domain_name = regExp.exec(issue.url)[1]
        if (issue.author.includes(String(name)) || issue.template_creator.includes(String(name))) {
            var container = create_issue(issue.url, domain_name, issue.author, issue.template_creator, issue.comment, issue.creator_comment);
            list.appendChild(container);
        }
    }
}

function filter_comment(text) {
    list = document.getElementById("main-list");
    list.innerHTML = "";

    for (i = 0; i < issue_data.length; i++) {
        var issue = issue_data[i];
        var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
        var domain_name = regExp.exec(issue.url)[1]
        if (issue.comment.includes(String(text)) || issue.creator_comment.includes(String(text))) {
            var container = create_issue(issue.url, domain_name, issue.author, issue.template_creator, issue.comment, issue.creator_comment);
            list.appendChild(container);
        }
    }
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

function search() {
    var text = document.getElementById("domain-search-bar").value;
    if (text === "") {
        remove_filter();
    } else {
        filter(text);
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
    issue_data = data;
    var list = document.getElementById("main-list");

    //var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;

    data.forEach(issue => {              
        var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
        var container = create_issue(issue.url, regExp.exec(issue.url)[1], issue.author, issue.template_creator, issue.comment, issue.creator_comment);
        list.appendChild(container);
    }); 

  })
  .catch(err => {
    // Do something for an error here
    console.error(err);
  })
