using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Security.Principal;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.Win32;

[assembly: AssemblyTitle("文墨工作台")]
[assembly: AssemblyProduct("文墨工作台")]
[assembly: AssemblyVersion("4.2.0.0")]
[assembly: AssemblyFileVersion("4.2.0.0")]

static class Desktop
{
    const string Name = "文墨工作台";
    const string Version = "4.2 测试版";
    const string Marker = ".wenmo-install";
    const string UninstallKey = @"Software\Microsoft\Windows\CurrentVersion\Uninstall\WenmoStudio";
    static readonly string Local = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
    static readonly string DefaultInstall = Path.Combine(Local, "Programs", "WenmoStudio");
    static readonly string UserData = Path.Combine(Local, "WenmoStudio");
    static readonly string Menu = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Programs), Name);
    static readonly Regex ServerUrl = new Regex(@"http://127\.0\.0\.1:[1-9]\d{0,4}\b");

    [STAThread]
    static int Main(string[] args)
    {
        try
        {
            if (args.Length == 2 && args[0] == "--test-install")
                return TestInstall(args[1]);
            if (args.Length == 2 && args[0] == "--test-launch")
                return TestLaunch(args[1]);
#if !SETUP && !REMOVE
            if (args.Length == 2 && args[0] == "--after-setup")
                WaitForExit(Int32.Parse(args[1]));
#endif
#if REMOVE
            if (args.Length == 2 && args[0] == "--remove")
                return RemoveInstallation(Int32.Parse(args[1]));
#endif
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            bool ownsLock;
            string lockName = @"Local\WenmoStudio.Desktop." + WindowsIdentity.GetCurrent().User.Value;
            using (var single = new Mutex(true, lockName, out ownsLock))
            {
                if (!ownsLock)
                {
#if !SETUP && !REMOVE
                    string running = ReadServerAddress();
                    if (running != null)
                    {
                        OpenBrowser(running);
                        return 0;
                    }
#endif
                    MessageBox.Show("请先退出正在运行的文墨工作台或安装程序。", Name);
                    return 1;
                }
#if SETUP
                ShowInstaller();
#elif REMOVE
                QueueUninstall();
#else
                Application.Run(new WorkbenchWindow());
#endif
            }
            return 0;
        }
        catch (Exception error)
        {
            if (args.Length == 0)
                MessageBox.Show(error.Message, Name, MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }

    static string Quote(string path) { return "\"" + path + "\""; }

    static string ReadServerAddress()
    {
        string path = Path.Combine(UserData, "server.url");
        if (!File.Exists(path)) return null;
        string text = File.ReadAllText(path).Trim();
        Match match = ServerUrl.Match(text);
        return match.Success && match.Value == text ? text : null;
    }

    static void OpenBrowser(string url)
    {
        Process.Start(new ProcessStartInfo(url) { UseShellExecute = true });
    }

    static Form BaseWindow(string title, int height)
    {
        return new Form {
            Text = title, ClientSize = new Size(454, height), StartPosition = FormStartPosition.CenterScreen,
            FormBorderStyle = FormBorderStyle.FixedDialog, MinimizeBox = true, MaximizeBox = false,
            Font = new Font("Microsoft YaHei UI", 9F), BackColor = Color.FromArgb(245, 248, 255),
            Icon = SystemIcons.Application, AutoScaleMode = AutoScaleMode.Dpi
        };
    }

    static Label TextBlock(string text, int top, int height, bool heading)
    {
        var label = new Label { Text = text, Left = 24, Top = top, Width = 405, Height = height,
            ForeColor = Color.FromArgb(25, 39, 75) };
        if (heading) label.Font = new Font("Microsoft YaHei UI", 16F, FontStyle.Bold);
        return label;
    }

    static Button ActionButton(string text, int left, int top)
    {
        return new Button { Text = text, Left = left, Top = top, Width = 105, Height = 34 };
    }

    static void ShowInstaller()
    {
        using (Form form = BaseWindow("安装 · " + Name, 266))
        {
            string previousInstall = RegisteredInstall();
            var heading = TextBlock(Name + "  " + Version, 22, 35, true);
            var detail = TextBlock("安装到当前账户。Python 和 PDF 组件已包含在安装包中。", 70, 34, false);
            var location = TextBlock("安装位置", 108, 22, false);
            var directory = new TextBox { Left = 24, Top = 133, Width = 288,
                Text = previousInstall ?? DefaultInstall, AccessibleName = "安装位置" };
            var browse = ActionButton("浏览…", 324, 127);
            var launch = new CheckBox { Text = "安装后打开工作台", Checked = true, Left = 24, Top = 176, Width = 230 };
            var cancel = ActionButton("取消", 208, 214);
            var install = ActionButton("安装", 324, 214);
            browse.Click += delegate {
                using (var picker = new FolderBrowserDialog())
                {
                    picker.Description = "选择程序文件夹的上一级目录。安装器会创建 WenmoStudio 文件夹。";
                    picker.ShowNewFolderButton = true;
                    string parent = null;
                    try { parent = Path.GetDirectoryName(directory.Text.Trim()); }
                    catch (ArgumentException) { }
                    if (Directory.Exists(parent)) picker.SelectedPath = parent;
                    if (picker.ShowDialog(form) == DialogResult.OK)
                        directory.Text = Path.Combine(picker.SelectedPath, "WenmoStudio");
                }
            };
            cancel.Click += delegate { form.Close(); };
            install.Click += delegate {
                install.Enabled = false;
                cancel.Enabled = false;
                try
                {
                    string destination = InstallPath(directory.Text);
                    bool relocating = previousInstall != null && !String.Equals(previousInstall, destination, StringComparison.OrdinalIgnoreCase);
                    if (relocating && (Inside(previousInstall, destination) || Inside(destination, previousInstall)))
                        throw new IOException("请选择与原安装文件夹独立的位置。");
                    InstallFiles(destination);
                    Register(destination);
                    if (relocating && OwnedInstall(previousInstall)) TryDeleteDirectory(previousInstall);
                    // Start the app after the installer releases the single-instance lock.
                    if (launch.Checked)
                    {
                        var start = new ProcessStartInfo(Path.Combine(destination, "WenmoStudio.exe"), "--after-setup " + Process.GetCurrentProcess().Id);
                        start.UseShellExecute = false;
                        Process.Start(start);
                    }
                    else
                        MessageBox.Show("安装完成。可以从开始菜单打开文墨工作台。", Name);
                    form.Close();
                }
                catch (Exception error)
                {
                    MessageBox.Show(error.Message, Name, MessageBoxButtons.OK, MessageBoxIcon.Error);
                    install.Enabled = true;
                    cancel.Enabled = true;
                }
            };
            form.Controls.AddRange(new Control[] { heading, detail, location, directory, browse, launch, cancel, install });
            form.AcceptButton = install;
            Application.Run(form);
        }
    }

    static int TestInstall(string target)
    {
#if SETUP
        target = InstallPath(target);
        if (Directory.Exists(target) && !OwnedInstall(target) && !EmptyDirectory(target)) return 2;
        InstallFiles(target);
        return 0;
#else
        return 2;
#endif
    }

    static void InstallFiles(string target)
    {
        if (Directory.Exists(target) && !OwnedInstall(target) && !EmptyDirectory(target))
            throw new IOException("安装目标已经存在其他文件，安装已停止。");
        string stage = target + ".staging-" + Guid.NewGuid().ToString("N");
        string backup = target + ".backup-" + Guid.NewGuid().ToString("N");
        Directory.CreateDirectory(stage);
        try
        {
            using (Stream payload = Assembly.GetExecutingAssembly().GetManifestResourceStream("WenmoPayload.zip"))
            {
                if (payload == null) throw new IOException("安装文件不完整。");
                using (var zip = new ZipArchive(payload, ZipArchiveMode.Read))
                    zip.ExtractToDirectory(stage);
            }
            if (!OwnedInstall(stage) || !File.Exists(Path.Combine(stage, "runtime", "python.exe")))
                throw new IOException("安装文件校验失败。");
            if (Directory.Exists(target)) Directory.Move(target, backup);
            try { Directory.Move(stage, target); }
            catch
            {
                if (Directory.Exists(backup) && !Directory.Exists(target)) Directory.Move(backup, target);
                throw;
            }
            if (OwnedInstall(backup) || EmptyDirectory(backup)) TryDeleteDirectory(backup);
        }
        finally { TryDeleteDirectory(stage); }
    }

    static bool OwnedInstall(string folder)
    {
        return Directory.Exists(folder) && (File.GetAttributes(folder) & FileAttributes.ReparsePoint) == 0 &&
            File.Exists(Path.Combine(folder, Marker)) && File.Exists(Path.Combine(folder, "WenmoStudio.exe")) &&
            File.Exists(Path.Combine(folder, "Uninstall.exe"));
    }

    static bool EmptyDirectory(string path)
    {
        return Directory.Exists(path) && (File.GetAttributes(path) & FileAttributes.ReparsePoint) == 0 &&
            !System.Linq.Enumerable.Any(Directory.EnumerateFileSystemEntries(path));
    }

    static string InstallPath(string text)
    {
        string path = text.Trim();
        if (!Path.IsPathRooted(path) || path.StartsWith(@"\\", StringComparison.Ordinal) ||
            !Regex.IsMatch(path, @"^[A-Za-z]:[\\/]"))
            throw new IOException("请输入本机磁盘上的完整安装路径。");
        string full = Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar);
        if (full.Length <= 3 || String.Equals(full, UserData, StringComparison.OrdinalIgnoreCase)
            || Inside(UserData, full) || Inside(full, UserData))
            throw new IOException("请选择单独的程序文件夹，历史数据目录会保留。");
        return full;
    }

    static bool Inside(string parent, string child)
    {
        return child.StartsWith(parent.TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar,
            StringComparison.OrdinalIgnoreCase);
    }

    static string RegisteredInstall()
    {
        using (RegistryKey key = Registry.CurrentUser.OpenSubKey(UninstallKey))
        {
            string value = key == null ? null : key.GetValue("InstallLocation") as string;
            if (String.IsNullOrWhiteSpace(value)) return null;
            try
            {
                string location = InstallPath(value);
                return OwnedInstall(location) ? location : null;
            }
            catch (IOException) { return null; }
            catch (ArgumentException) { return null; }
        }
    }

    static void TryDeleteDirectory(string path)
    {
        if (Directory.Exists(path) && (File.GetAttributes(path) & FileAttributes.ReparsePoint) == 0)
        {
            try { Directory.Delete(path, true); }
            catch (IOException) { }
            catch (UnauthorizedAccessException) { }
        }
    }

    static void Register(string target)
    {
        Directory.CreateDirectory(Menu);
        dynamic shell = Activator.CreateInstance(Type.GetTypeFromProgID("WScript.Shell"));
        dynamic shortcut = shell.CreateShortcut(Path.Combine(Menu, Name + ".lnk"));
        shortcut.TargetPath = Path.Combine(target, "WenmoStudio.exe");
        shortcut.WorkingDirectory = target;
        shortcut.Save();
        using (RegistryKey key = Registry.CurrentUser.CreateSubKey(UninstallKey))
        {
            key.SetValue("DisplayName", Name);
            key.SetValue("DisplayVersion", Version);
            key.SetValue("InstallLocation", target);
            key.SetValue("DisplayIcon", Path.Combine(target, "WenmoStudio.exe") + ",0");
            key.SetValue("UninstallString", Quote(Path.Combine(target, "Uninstall.exe")));
            key.SetValue("NoModify", 1, RegistryValueKind.DWord);
            key.SetValue("NoRepair", 1, RegistryValueKind.DWord);
        }
    }

    static void QueueUninstall()
    {
        if (MessageBox.Show("卸载文墨工作台？历史文稿和 Token 用量将保留在本地。", Name,
            MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return;
        string temporary = Path.Combine(Path.GetTempPath(), "WenmoStudio-Uninstall-" + Guid.NewGuid().ToString("N") + ".exe");
        File.Copy(Assembly.GetExecutingAssembly().Location, temporary);
        Process.Start(new ProcessStartInfo(temporary, "--remove " + Process.GetCurrentProcess().Id) { UseShellExecute = false });
    }

    static int RemoveInstallation(int installerPid)
    {
        WaitForExit(installerPid);
        bool exclusive;
        using (var guard = new Mutex(true, @"Local\WenmoStudio.Desktop." + WindowsIdentity.GetCurrent().User.Value, out exclusive))
        {
            string target = RegisteredInstall();
            if (!exclusive || target == null)
            {
                MessageBox.Show("请退出文墨工作台后重新卸载。", Name);
                return 1;
            }
            Directory.Delete(target, true);
            File.Delete(Path.Combine(Menu, Name + ".lnk"));
            if (Directory.Exists(Menu) && Directory.GetFileSystemEntries(Menu).Length == 0) Directory.Delete(Menu);
            Registry.CurrentUser.DeleteSubKeyTree(UninstallKey, false);
            MessageBox.Show("卸载完成。历史文稿和 Token 用量仍保存在本地。", Name);
            return 0;
        }
    }

    static void WaitForExit(int pid)
    {
        try { using (Process creator = Process.GetProcessById(pid)) creator.WaitForExit(18000); }
        catch (ArgumentException) { }
    }

    static Process StartBackend(string location, string data, TaskCompletionSource<string> ready)
    {
        Directory.CreateDirectory(data);
        var process = new Process();
        process.StartInfo = new ProcessStartInfo {
            FileName = Path.Combine(location, "runtime", "python.exe"), WorkingDirectory = location,
            Arguments = "-X utf8 -B -u " + Quote(Path.Combine(location, "wenmo.py")) +
                " --no-browser --stop-on-stdin-close --data " + Quote(Path.Combine(data, "wenmo.sqlite3")),
            UseShellExecute = false, CreateNoWindow = true, RedirectStandardInput = true,
            RedirectStandardOutput = true, RedirectStandardError = true,
            StandardOutputEncoding = Encoding.UTF8, StandardErrorEncoding = Encoding.UTF8
        };
        process.EnableRaisingEvents = true;
        process.Exited += delegate { ready.TrySetException(new IOException("无法启动本地服务。请检查目录权限或重新安装。")); };
        process.OutputDataReceived += delegate(object sender, DataReceivedEventArgs evt) {
            Match match = ServerUrl.Match(evt.Data ?? "");
            if (match.Success) ready.TrySetResult(match.Value);
        };
        process.ErrorDataReceived += delegate { };
        process.Start();
        process.BeginOutputReadLine();
        process.BeginErrorReadLine();
        return process;
    }

    static void StopBackend(Process process)
    {
        if (process == null) return;
        using (process)
        {
            if (process.HasExited) return;
            try
            {
                process.StandardInput.Close();
                if (!process.WaitForExit(3500)) process.Kill();
            }
            catch (InvalidOperationException) { }
            catch (IOException) { }
        }
    }

    static int TestLaunch(string dataRoot)
    {
        string data = Path.GetFullPath(dataRoot);
        var ready = new TaskCompletionSource<string>();
        Process host = StartBackend(AppDomain.CurrentDomain.BaseDirectory, data, ready);
        try
        {
            if (!ready.Task.Wait(15000)) return 3;
            if (!File.Exists(Path.Combine(data, "wenmo.sqlite3"))) return 4;
            File.WriteAllText(Path.Combine(data, "ready.txt"), ready.Task.Result, Encoding.ASCII);
            return 0;
        }
        finally { StopBackend(host); }
    }

    sealed class WorkbenchWindow : Form
    {
        readonly Label status;
        readonly Button browser;
        Process host;
        string url;
        bool closing;

        public WorkbenchWindow()
        {
            Text = Name + " · " + Version;
            ClientSize = new Size(454, 176);
            StartPosition = FormStartPosition.CenterScreen;
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            Font = new Font("Microsoft YaHei UI", 9F);
            Icon = SystemIcons.Application;
            Controls.Add(TextBlock(Name, 17, 37, true));
            status = TextBlock("正在启动本地工作台…", 63, 58, false);
            browser = ActionButton("打开网页", 208, 124);
            browser.Enabled = false;
            browser.Click += delegate { TryOpenBrowser(); };
            var exit = ActionButton("退出", 324, 124);
            exit.Click += delegate { Close(); };
            Controls.AddRange(new Control[] { status, browser, exit });
            Shown += Start;
            FormClosing += delegate {
                closing = true;
                StopBackend(host);
                host = null;
                try { File.Delete(Path.Combine(UserData, "server.url")); }
                catch (IOException) { }
                catch (UnauthorizedAccessException) { }
            };
        }

        async void Start(object sender, EventArgs args)
        {
            var ready = new TaskCompletionSource<string>();
            try
            {
                File.Delete(Path.Combine(UserData, "server.url"));
                host = StartBackend(AppDomain.CurrentDomain.BaseDirectory, Path.Combine(UserData, "data"), ready);
                if (await Task.WhenAny(ready.Task, Task.Delay(15000)) != ready.Task)
                    throw new IOException("等待本地服务启动超时。");
                if (closing) return;
                url = await ready.Task;
                File.WriteAllText(Path.Combine(UserData, "server.url"), url, Encoding.ASCII);
                status.Text = "工作台已启动\n" + url + "\n关闭本窗口会停止本地服务。";
                browser.Enabled = true;
                TryOpenBrowser();
            }
            catch (Exception error)
            {
                if (closing) return;
                StopBackend(host);
                host = null;
                status.Text = error.Message;
            }
        }

        void TryOpenBrowser()
        {
            if (url == null) return;
            try { OpenBrowser(url); }
            catch (Exception) { status.Text = "请在浏览器地址栏输入 " + url; }
        }
    }
}
