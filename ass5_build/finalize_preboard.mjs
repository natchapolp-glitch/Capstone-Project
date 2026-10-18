import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const root=process.cwd();
const skill='C:/Users/NATCHAPOL/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const runtime='C:/Users/NATCHAPOL/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const privateDir=path.join(root,'.codex-finalizer');
await fs.mkdir(privateDir,{recursive:true});
const candidate=path.join(privateDir,'preboard-candidate.pptx');
await fs.copyFile(path.join(process.env.USERPROFILE,'SeminarLab/preboard/document_review/revision/Ass5_DRAFT.pptx'),candidate);
const referencePath=path.join(root,'ass5_output/Residential_Intelligence_Project_Progress_READY_2026-10-18.pptx');
const finalPath=path.join(root,'ass5_output',process.argv[2]||'Residential_Intelligence_Project_Progress_REVIEWED_2026-10-18.pptx');
await fs.mkdir(path.dirname(finalPath),{recursive:true});
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({
 workspaceDir:root,candidatePath:candidate,finalPath,
 pythonExecutable:path.join(runtime,'python/python.exe'),
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12191695,6858000','--validate-bullet-geometry','--validate-heading-fit',... [17,18,19].flatMap(x=>['--require-native-table-slide',String(x)])],
 requiredNativeTableOwnerSlides:[17,18,19],
 fontPolicy:{basis:'reference',families:['Tahoma'],referencePath,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(referencePath)).digest('hex')},
 verifyArtifactToolImport:true,
 receiptPath:path.join(privateDir,path.basename(finalPath)+'.validation.json'),
});
console.log(JSON.stringify(result));
