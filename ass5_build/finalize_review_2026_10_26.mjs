import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const root=process.cwd(), skill='C:/Users/NATCHAPOL/.codex/plugins/cache/openai-primary-runtime/presentations/26.1025.11240/skills/presentations';
const runtime='C:/Users/NATCHAPOL/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const referencePath=path.join(root,'DEMO_PRESENTATION_2026-10-21/Residential_Intelligence_Project_Progress_REVIEWED_2026-10-18.pptx');
const finalPath=path.join(root,'PRESENTATION_READY_2026-10-26/Ass5_REVIEWED_2026-10-26.pptx');
await fs.mkdir(path.dirname(finalPath),{recursive:true});
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir:root,candidatePath:path.join(root,'.codex-finalizer/review-2026-10-26/candidate.pptx'),finalPath,
 explicitTotalSlideCount:21,pythonExecutable:path.join(runtime,'python/python.exe'),
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12191695,6858000','--validate-bullet-geometry','--validate-heading-fit',...[17,18,19].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:[17,18,19],
 fontPolicy:{basis:'reference',families:['Tahoma'],referencePath,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(referencePath)).digest('hex')},
 verifyArtifactToolImport:true,receiptPath:path.join(root,'.codex-finalizer/review-2026-10-26/validation.json')});
console.log(JSON.stringify(result));
