const { Index, Document, Worker,FlexSearch } = require("flexsearch");
const { parse }=require("node-html-parser");



let org_keyword="Type 'Plugin meet' in the textbox ->Google Search"
let keyword=org_keyword.split('->')[1]

let cnt=0
function recur(root,ans,index){
    let counter=0;
    let map={}
    if(!root | typeof(root) === 'undefined' ){
        return
    }

    for(let i=0;i<root.childNodes.length;i++){
            index.add(cnt,root.childNodes[i].outerHTML)
            map[cnt]=i
    }

    const new_root_idx_arr=index.search(keyword)

    for(let j=0;j<new_root_idx_arr.length;j++){
        if(root.childNodes[map[new_root_idx_arr[j]]]  && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='iframe' && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='script' && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='picture' && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='style' && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='code' && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='img' && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='use'){
            const index_to_remove = ans.indexOf(root.childNodes[map[new_root_idx_arr[j]]].parentNode);
            if (index_to_remove > -1) {
                ans.splice(index_to_remove, 1);
            }

            const index_to_add=ans.indexOf(root.childNodes[map[new_root_idx_arr[j]]])
            if(index_to_add==-1){
                ans.push(root.childNodes[map[new_root_idx_arr[j]]])
                recur(root.childNodes[map[new_root_idx_arr[j]]],ans,index)
            }
        }

    }
    return
}
const fs = require('fs')

function dom_extractor(){
    const dom_content = fs.readFileSync("dom_content.txt", "utf-8")
    const goal = fs.readFileSync("goal.txt", "utf-8")
    return dom_content
    const root = parse(dom_content);
    org_keyword = goal
    keyword=org_keyword.split('->')[1]
    const index = new Index({tokenize:"strict",resolution:9});

    const ans=[]
    let relevant_elements=[]
    for(let i=0;i<root.childNodes.length;i++){
        if( root.childNodes[i].rawTagName!='script'){
            relevant_elements.push(root.childNodes[i])
        }
    }

    for(let i=0;i<relevant_elements.length;i++){
        recur(relevant_elements[i],ans,index)
    }
    let res = ""
    for(let i=0;i<ans.length;i++){
        res += ans[i].outerHTML + "\n"
    }
    return res
}
